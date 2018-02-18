
from ..parser.tokens import OPERATOR
from .opcodes import AnyOpCode


class Code(AnyOpCode):
	transform = property(lambda self: self.compile)

	def __init__(self, buff, rules, scope):
		self.buff = buff
		self.rules = rules
		self.scope = scope

	def get(self, index, default=None):
		try:
			return self[index]
		except IndexError:
			return default

	def get_subcode(self, idx_start, idx_end):
		subcode = self.create(self.buff[idx_start:idx_end])
		del self[idx_start:idx_end]
		return subcode

	def insert(self, index, opcode):
		self.buff.insert(index, opcode)

	def extend(self, buff):
		if buff and Definition == buff[0]:
			self.add_definition(len(self), buff.pop(0))
		self.buff.extend(buff)

	def append(self, buff):
		self.buff.append(buff)

	def index(self, opcode):
		return self.buff.index(opcode)

	def add_definition(self, idx, opcodes):
		while (idx > 0) and (self.get(idx) != OPERATOR('line_end')):
			idx -= 1
		if idx != 0:
			idx += 1
		if Definition != self[idx]:
			self.insert(idx, self.create_definition())
		self[idx].extend(opcodes)

	def compile(self):
		while self.__apply_rule():
			pass
		while self.__after_compile():
			pass

	def pop(self, index):
		return self.buff.pop(index)

	def create(self, buff=None, type_code=None):
		buff = [] if buff is None else list(buff)
		type_code = type(self) if type_code is None else type_code
		return type_code(buff=buff, rules=self.rules, scope=self.scope)

	def create_definition(self, buff=None):
		return self.create(buff, type_code=Definition)

	def __apply_rule(self):
		for idx_start, _ in enumerate(self.buff):
			for rule in self.rules:
				result_match = rule.match(self, self.buff[idx_start:])
				if result_match:
					result = rule(self, idx_start, result_match.idx_end)
					if rule.in_context:
						return True
					if (len(result) > 1) and (Definition == result[0]):
						definition = result[0]
						result = result[1:]
						self.buff[idx_start:idx_start+result_match.idx_end] = result
						self.add_definition(idx_start, definition)
					else:
						self.buff[idx_start:idx_start+result_match.idx_end] = result
					return True

	def __after_compile(self):
		for idx, opcode in enumerate(self.buff):
			if OPERATOR('line_end') == opcode:
				del self.buff[idx]
				return True
			elif Code == opcode:
				opcode.compile()
			elif hasattr(opcode, 'code'):
				opcode.code.compile()

	def __iter__(self):
		return iter(self.buff)

	def __getitem__(self, index):
		buff = self.buff[index]
		if isinstance(index, slice):
			return self.create(buff)
		return buff

	def __setitem__(self, index, elem):
		self.buff[index] = elem

	def __delitem__(self, index):
		del self.buff[index]

	def __len__(self):
		return len(self.buff)

	def __hash__(self):
		return hash(tuple(self))

	def __bool__(self):
		return bool(self.buff)

	def __repr__(self, is_lazy=False):
		if is_lazy:
			def generator():
				yield f'{type(self).__name__}:\n'
				for opcode in self:
					if Code == opcode:
						for repr_opcode in opcode.__repr__(True):
							yield '   ' + repr_opcode
					else:
						yield '   ' + repr(opcode) + '\n'
			return generator()
		return ''.join(self.__repr__(True))


class Definition(Code):
	pass

