from actl.Buffer import Buffer
from actl.syntax import Token, BufferRule


class Parser:
	def __init__(self, scope, rules, buff, endLine=Token('\n'),):
		self.scope = scope
		self.rules = rules
		self.buff = buff
		self.endLine = endLine
		self.definition = Buffer()

	def define(self, *opcodes):
		self.definition.append(*opcodes)

	def subParser(self, buff, endLine=None):
		if endLine is None:
			endLine = self.endLine

		return type(self)(self.scope, self.rules, buff, endLine)

	def _applyRule(self):
		for rule in self.rules:
			res = rule(self, self.buff)
			if res:
				return res
		return None

	def parseLine(self, insertDefiniton=True):
		flush = Buffer()

		while (self.endLine not in BufferRule(self, flush)) and self.buff:
			res = self._applyRule()
			if res is None:
				flush.append(self.buff.pop())
				continue

			self.buff.insert(0, (flush + res))
			flush = Buffer()

		res = BufferRule(self, flush).popUntil(self.endLine)
		self.buff.insert(0, flush)

		if insertDefiniton:
			self.buff.insert(0, self.definition + res)
		else:
			self.buff.insert(0, res)

	def __iter__(self):
		while self.buff:
			self.parseLine()
			self.definition = Buffer()
			res = BufferRule(self, self.buff).popUntil(self.endLine)
			BufferRule(self, self.buff).pop(self.endLine, default=None)
			yield from res

	def __str__(self):
		return f'Parser<{self.__dict__}>'
