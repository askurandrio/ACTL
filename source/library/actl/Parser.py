
from actl.code.opcodes import END_LINE
from .Buffer import Buffer
from .util import ResultIsBuffer


class parser(metaclass=ResultIsBuffer):
	def __init__(self, buff, rules):
		self._buff = buff
		self._rules = rules
		self._definition = Buffer()

	def define(self, *opcodes):
		self._definition.append(*opcodes)

	def _apply_rule(self, buff):
		for rule in self._rules:
			res = rule(buff)
			if res:
				res(self)
				return True
		return False

	def _parse_definition(self):
		while self._definition:
			if self._apply_rule(self._definition):
				continue
			yield self._definition.pop()
		
	def __iter__(self):
		flush = Buffer()
		while self._buff:
			if self._apply_rule(self._buff):
				continue
			flush.append(self._buff.pop())
			if END_LINE in flush:
				idx_end_line = flush.index(END_LINE)
				res = flush[:idx_end_line]
				del flush[:idx_end_line]
				yield from self._parse_definition()
				yield from res
		yield from self._parse_definition()
		yield from flush
