from actl.Buffer import Buffer
from actl.syntax import Token, BufferRule


class Parser:

	def __init__(self, scope, rules, buff, endLine=Token('\n')):
		self.scope = scope
		self.rules = rules
		self.buff = buff
		self._endLine = endLine
		self._definition = Buffer()

	def define(self, *opcodes):
		self._definition.append(*opcodes)

	def subParser(self, buff, endLine=None):
		if endLine is None:
			endLine = self._endLine

		return type(self)(self.scope, self.rules, buff, endLine)

	def _applyRule(self):
		for rule in self.rules:
			res = rule(self, self.buff)
			if res:
				return res
		return None

	def parseLine(self):
		flush = Buffer()
		while (self._endLine not in BufferRule(self, flush)) and self.buff:
			res = self._applyRule()
			if res is None:
				flush.append(self.buff.pop())
				continue

			self.buff.appFront(*(flush + res))
			flush = Buffer()

		res = BufferRule(self, flush).popUntil(self._endLine)
		self.buff.appFront(*flush)

		res = self._definition + res
		self._definition = Buffer()
		return res

	def __iter__(self):
		while self.buff:
			res = self.parseLine()
			if self.buff and (self.buff[0] == '\n'):
				self.buff.pop()
			yield from res
