
from .opcodes import AnyOpCode
from .opcodes.opcodes import Word, Operator


class Code(AnyOpCode):
	def __init__(self, buff, rules):
		self.buff = buff
		self.rules = rules

	def insert(self, index, opcode):
		self.buff.insert(index, opcode)

	def compile(self):
		while self.__apply_rule():
			pass
		while self.__after_compile():
			pass

	def __apply_rule(self):
		for idx, _ in enumerate(self.buff):
			for rule in self.rules:
				idx_end = rule.match(self.buff[idx:])
				if idx_end is not None:
					result = rule(self, idx, self.buff[idx:idx+idx_end])
					if rule.in_context:
						pass
					else:
						self.buff[idx:idx+idx_end] = result
					return True

	def __after_compile(self):
		for idx, opcode in enumerate(self.buff):
			if Operator('line_end') == opcode:
				del self.buff[idx]
				return True
			#assert opcode in (Word, Operator), f'{opcode} in {(Word, Operator)}'

	def __repr(self):
		yield 'Code:\n'
		for opcode in self:
			if isinstance(opcode, type(self)):
				for repr_opcode in opcode.__repr():
					yield '   ' + repr_opcode
			else:
				yield '   ' + repr(opcode) + '\n'

	def __iter__(self):
		return iter(self.buff)

	def __getitem__(self, index):
		buff = self.buff.__getitem__(index)
		if isinstance(index, slice):
			return type(self)(buff, self.rules)
		return buff

	def __delitem__(self, index):
		return self.buff.__delitem__(index)

	def __bool__(self):
		return bool(self.buff)

	def __repr__(self):
		return ''.join(self.__repr())
