
from actl.opcodes import END_LINE
from actl.Buffer import Buffer


class Parser:
	def __init__(self, scope, rules, buff):
		self.scope = scope
		self._rules = rules
		self._buff = buff
		self._definition = Buffer()

	def define(self, *opcodes):
		self._definition.append(*opcodes)

	def subParse(self, buff):
		parser = type(self)(self.scope, self._rules, None)
		return parser.parseLine(buff)

	def _apply_rule(self, buff):
		for rule in self._rules:
			res = rule(self, buff)
			if res:
				return True
		return False

	def parseLine(self, buff):
		flush = Buffer()
		while buff and (END_LINE not in flush):
			if self._apply_rule(buff):
				buff = flush + buff
				flush = Buffer()
				continue

			flush.append(buff.pop())

		if END_LINE in flush:
			idx_end_line = flush.index(END_LINE)
			res = flush[:idx_end_line]
			del flush[:idx_end_line]
		else:
			res = flush
			flush = Buffer()

		res = self._definition + res
		self._definition = Buffer()
		newBuff = flush + buff
		return res, newBuff

	def __iter__(self):
		while self._buff:
			res, self._buff = self.parseLine(self._buff)
			yield from res
