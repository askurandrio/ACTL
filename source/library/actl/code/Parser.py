
from ..tokenizer.tokens import OPERATOR
from .Code import Code, Definition


class Parser:
	def __init__(self, code, rules):
		self.code = code
		self.rules = rules

	def is_matching(self):
		for idx_start, _ in enumerate(self.code):
			for rule in self.rules:
				result_match = rule.match(self.code, self.code[idx_start:])
				if result_match or result_match.is_matching():
					return True
		return False

	def link(self):
		while self.__apply_rule():
			pass
		while self.__after_compile():
			pass
		return 'next'

	def __apply_rule(self):
		for idx_start, _ in enumerate(self.code):
			for rule in self.rules:
				result_match = rule.match(self.code, self.code[idx_start:])
				if result_match:
					result = rule(self.code, idx_start, result_match.idx_end)
					if rule.in_context:
						return True
					if (len(result) > 1) and (Definition == result[0]):
						definition = result[0]
						result = result[1:]
						self.code[idx_start:idx_start+result_match.idx_end] = result
						self.code.add_definition(idx_start, definition)
					else:
						self.code[idx_start:idx_start+result_match.idx_end] = result
					return True

	def __after_compile(self):
		for idx, opcode in enumerate(self.code):
			if OPERATOR('line_end') == opcode:
				del self.code[idx]
				return True
			elif Code == opcode:
				type(self)(opcode, self.rules).link()
			elif hasattr(opcode, 'code'):
				type(self)(opcode.code, self.rules).link()
