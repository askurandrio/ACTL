from contextlib import contextmanager

from actl.Buffer import Buffer
from actl.syntax import Token, BufferRule
from actl.opcodes import VARIABLE


class Parser:
	def __init__(self, scope, rules, buff, endLine=Token('\n'), makeTmpVar=None):
		self.scope = scope
		self.rules = rules
		self.buff = buff
		self.endLine = endLine
		self.definition = Buffer()
		if makeTmpVar is None:
			makeTmpVar = _TmpVarFactory()
		self.makeTmpVar = makeTmpVar

	def define(self, *opcodes):
		self.definition.append(*opcodes)

	def subParser(self, buff, endLine=None):
		if endLine is None:
			endLine = self.endLine

		return type(self)(self.scope, self.rules, buff, endLine, self.makeTmpVar)

	def _applyRule(self):
		apply = self.rules.match(self, self.buff)
		if apply:
			apply()
			return True
		return False

	def parseLine(self, insertDefiniton=True):
		flush = Buffer()

		while (self.endLine not in BufferRule(self, flush)) and self.buff:
			isApplied = self._applyRule()
			if isApplied:
				self.buff.insert(0, flush)
				flush = Buffer()
				continue

			flush.append(self.buff.pop())

		res = BufferRule(self, flush).popUntil(self.endLine)
		self.buff.insert(0, flush)

		if insertDefiniton:
			self.buff.insert(0, self.definition + res)
		else:
			self.buff.insert(0, res)

	def __iter__(self):
		while self.buff:
			with self.makeTmpVar:
				self.parseLine()
			self.definition = Buffer()
			res = BufferRule(self, self.buff).popUntil(self.endLine)
			BufferRule(self, self.buff).pop(self.endLine, default=None)
			yield from res

	def __str__(self):
		return f'Parser<{self.__dict__}>'


class _TmpVarFactory:
	def __init__(self):
		self._counter = 0
		self._contextCounter = 0
		self._nestedScopeCounter = 0

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

		return VARIABLE(f'_tmpVar{scopeName}{self._counter}')

	def __enter__(self):
		self._contextCounter += 1

	def __exit__(self, *_):
		self._contextCounter -= 1
		if self._contextCounter == 0:
			self._counter = 0
