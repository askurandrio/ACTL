
from .opcodes import AnyOpCode
from .opcodes.opcodes import Word, Operator


class Code(AnyOpCode):
	def __init__(self, buff, rules):
		self.buff = buff
		self.rules = rules

	def compile(self):
		while self.__apply_rule():
			pass
		while self.__after_compile():
			pass

	def __apply_rule(self):
		for idx in range(len(self.buff)):
			for rule in self.rules:
				idx_end = rule.match(self.buff[idx:])
				if idx_end is not None:
					result = rule(self, idx, self.buff[idx:idx+idx_end+1])
					if (not rule.add_context) and (result is not None):
						self.buff[idx:idx+idx_end+1] = result
					return True

	def __after_compile(self):
		for idx, opcode in enumerate(self.buff):
			if Operator('line_end') == opcode:
				del self.buff[idx]
				return None
			#assert opcode in (Word, Operator), f'{opcode} in {(Word, Operator)}'

	def __iter__(self):
		return iter(self.buff)

	def __repr__(self, ident=4):
		result = ''
		result += 'Code:'
		for opcode in self:
			result += ('\n' + (' ' * ident))
			if isinstance(opcode, self.__class__):
				result += opcode.__repr__(ident + 4)
			else:
				result += repr(opcode)
		return result
