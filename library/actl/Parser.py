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
				return True
		return False

	def parseLine(self):
		flush = Buffer()
		while (self._endLine not in BufferRule(self, flush)) and self.buff:
			if self._applyRule():
				self.buff.set_(flush + self.buff)
				flush = Buffer()
				continue

			flush.append(self.buff.pop())

		if self._endLine in BufferRule(self, flush):
			idx_end_line = BufferRule(self, flush).index(self._endLine)
			res = flush[:idx_end_line]
			self.buff.set_(flush[idx_end_line:] + self.buff)
		else:
			res = flush

		res = self._definition + res
		self._definition = Buffer()
		return res

	def __iter__(self):
		while self.buff:
			res = self.parseLine()
			if self.buff and (self.buff[0] == '\n'):
				self.buff.pop()
			yield from res
