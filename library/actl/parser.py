from contextlib import contextmanager
import os

from actl.Buffer import Buffer
from actl.syntax import Token, BufferRule
from actl.opcodes import VARIABLE
from actl.utils import Inside, executeSyncCoroutine


class Parser:
	_LOG_APPLY = os.environ.get('ACTL_LOG_APPLY')
	if _LOG_APPLY:
		_INSIDE = Inside()

	def __init__(
		self,
		scope,
		rules,
		buff,
		endLine=Token('\n'),
		makeTmpVar=None,
		onLineStart=False,
	):
		self.scope = scope
		self.rules = rules
		self.buff = buff
		self.endLine = endLine
		self.definition = Buffer()
		if makeTmpVar is None:
			makeTmpVar = _TmpVarFactory()
		self.makeTmpVar = makeTmpVar
		self.onLineStart = onLineStart

	def define(self, *opcodes):
		self.definition.append(*opcodes)

	def _makeSyntaxError(self, message=''):
		message = f'Error during parsing at buff<{self.buff}>{message}'
		return RuntimeError(message)

	def subParser(self, buff, endLine=None):
		if endLine is None:
			endLine = self.endLine

		return type(self)(self.scope, self.rules, buff, endLine, self.makeTmpVar)

	async def _applyRule(self):
		if self._LOG_APPLY:
			buffRepr = str(self.buff)

		apply = await self.rules.match(self, self.buff)
		if apply:
			if self._LOG_APPLY:
				print(
					f'{self._INSIDE.indent()}{apply}\n{self._INSIDE.indent()}	before: {buffRepr}'
				)
				self._INSIDE.__enter__()
			try:
				await apply()
			except Exception as ex:
				raise self._makeSyntaxError(ex) from ex

			if self._LOG_APPLY:
				self._INSIDE.__exit__()
				print(
					f'{self._INSIDE.indent()}{self._INSIDE.indent()}	after: {self.buff}'
				)
			self.onLineStart = False
			return True
		return False

	async def parseUntilLineEnd(self, insertDefiniton=True, checkEndLineInBuff=False):
		flush = Buffer()

		while (not await BufferRule(self, flush).contains(self.endLine)) and self.buff:
			isApplied = await self._applyRule()
			if isApplied:
				self.buff.insert(0, flush)
				flush = Buffer()
				if checkEndLineInBuff and await BufferRule(self, self.buff).startsWith(
					self.endLine
				):
					return
				continue

			flush.append(self.buff.pop())

		res = tuple(
			await Buffer.loadAsync(BufferRule(self, flush).popUntil(self.endLine))
		)
		self.buff.insert(0, flush)

		if insertDefiniton:
			self.buff.insert(0, self.definition + res)
		else:
			self.buff.insert(0, res)

	async def parseLine(self):
		self.onLineStart = True
		with self.makeTmpVar:
			await self.parseUntilLineEnd()
		self.definition = Buffer()
		res = (
			await Buffer.loadAsync(BufferRule(self, self.buff).popUntil(self.endLine))
		).loadAll()
		return res

	def __iter__(self):
		while self.buff:
			res = executeSyncCoroutine(self.parseLine())
			for opcode in res:
				try:
					yield opcode
				except Exception as ex:
					raise self._makeSyntaxError(f'at res<{res}>') from ex
			executeSyncCoroutine(
				BufferRule(self, self.buff).pop(self.endLine, default=None)
			)

	def __str__(self):
		return f'Parser<{self.__dict__}>'


class _TmpVarFactory:
	_tmpVarPrefix = '_tmpVar'

	def __init__(self):
		self._counter = 0
		self._contextCounter = 0
		self._nestedScopeCounter = 0

	def isTmpVar(self, varName):
		return varName.startswith(self._tmpVarPrefix)

	@contextmanager
	def onNestedScope(self):
		prevCounter, self._counter = self._counter, 0
		self._nestedScopeCounter += 1
		yield
		self._nestedScopeCounter -= 1
		self._counter = prevCounter

	def __call__(self):
		self._counter += 1

		if self._nestedScopeCounter == 0:
			scopeName = ''
		else:
			scopeName = f'{self._nestedScopeCounter}_'

		return VARIABLE(f'{self._tmpVarPrefix}{scopeName}{self._counter}')

	def __enter__(self):
		self._contextCounter += 1

	def __exit__(self, *_):
		self._contextCounter -= 1
		if self._contextCounter == 0:
			self._counter = 0
