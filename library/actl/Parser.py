
from actl.opcodes import END_LINE
from actl.Buffer import Buffer


class Parser:
	def __init__(self, rules, buff):
		self._rules = rules
		self._buff = buff
		self._definition = Buffer()

	def define(self, *opcodes):
		self._definition.append(*opcodes)

	def _apply_rule(self, buff):
		for rule in self._rules:
			res = rule(buff)
			if res is not None:
				res(self)
				return True
		return False

	def __iter__(self):
		flush = Buffer()

		while self._buff:
			if self._apply_rule(self._buff):
				self._buff = flush.extract() + self._buff
				continue
			flush.append(self._buff.pop())
			if END_LINE in flush:
				idx_end_line = flush.index(END_LINE)
				res = flush[:idx_end_line]
				del flush[:idx_end_line]
				yield from self._definition.extract()
				yield from res
		yield from self._definition
		yield from flush
