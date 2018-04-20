
from ..tokenizer import tokens
from .Code import Code, Definition


class Parser:
	def __init__(self, buff, scope, rules):
		from actl import Buffer

		self.buff = Buffer(buff)
		self.scope = scope
		self.rules = rules

	def is_matching(self):
		for idx_start, _ in enumerate(self.buff):
			for rule in self.rules:
				result_match = rule.match(self.scope, self.buff[idx_start:])
				if result_match or result_match.is_matching():
					return idx_start - 1
		return None

	def parse(self):
		while self.is_matching() is not None:
			self.__apply_rule()
		while self.__after_compile():
			pass
		yield from self.buff

	def get_definition(self, idx):
		while (idx > 0) and \
				(tokens.OPERATOR('line_end') != self.buff.get(idx)) and \
				(tokens.INDENT != self.buff.get(idx)):
			idx -= 1
		if idx != 0:
			idx += 1
		if not isinstance(self.buff[idx], list):
			self.buff.insert(idx, Code())
		return self.buff[idx]

	def __apply_rule(self):
		for idx_start, _ in enumerate(self.buff):
			for rule in self.rules:
				result_match = rule.match(self.scope, self.buff[idx_start:])
				if result_match:
					result = rule(self.scope, self.buff.proxy(idx_start))
					if rule.in_context:
						return True
					self.__insert_result(idx_start, result)
					return True

	def __insert_result(self, idx_start, result):
		definition = None
		for opcode in result:
			if isinstance(opcode, Definition):
				if definition is None:
					definition = self.get_definition(idx_start)
					if not definition:
						idx_start += 1
				definition.append(opcode.elem)
			else:
				self.buff.insert(idx_start, opcode)
				idx_start += 1

	def __after_compile(self):
		for idx, opcode in enumerate(self.buff):
			if tokens.OPERATOR('line_end') == opcode:
				del self.buff[idx]
				return True
			elif isinstance(opcode, Code):
				type(self)(opcode, self.scope, self.rules).parse()
				return True
