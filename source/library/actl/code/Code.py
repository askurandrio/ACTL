
from .opcodes import AnyOpCode


class Code(AnyOpCode):
	def __init__(self, buff, scope):
		self.__buff = buff
		self.scope = scope

	def get(self, index, default=None):
		try:
			return self[index]
		except IndexError:
			return default

	def insert(self, index, opcode):
		self.__buff.insert(index, opcode)

	def extract(self, idx_start, idx_end):
		subcode = self[idx_start:idx_end]
		del self[idx_start:idx_end]
		return subcode

	def extend(self, buff):
		if buff and Definition == buff[0]:
			self.add_definition(len(self), buff.pop(0))
		self.__buff.extend(buff)

	def append(self, buff):
		self.__buff.append(buff)

	def index(self, opcode):
		return self.__buff.index(opcode)

	def add_definition(self, idx, opcodes):
		import actl

		while (idx > 0) and \
				(actl.tokenizer.tokens.OPERATOR('line_end') != self.get(idx)) and \
				(actl.tokenizer.tokens.INDENT != self.get(idx)):
			idx -= 1
		if idx != 0:
			idx += 1
		if Definition != self[idx]:
			self.insert(idx, self.create_definition())
		self[idx].extend(opcodes)

	def pop(self, index):
		return self.__buff.pop(index)

	def create(self, buff=None, type_code=None):
		buff = [] if buff is None else list(buff)
		type_code = type(self) if type_code is None else type_code
		return type_code(buff=buff, scope=self.scope)

	def create_definition(self, buff=None):
		return self.create(buff, type_code=Definition)

	def __iter__(self):
		return iter(self.__buff)

	def __getitem__(self, index):
		buff = self.__buff[index]
		if isinstance(index, slice):
			return self.create(buff)
		return buff

	def __setitem__(self, index, elem):
		self.__buff[index] = elem

	def __delitem__(self, index):
		del self.__buff[index]

	def __len__(self):
		return len(self.__buff)

	def __hash__(self):
		return hash(tuple(self))

	def __bool__(self):
		return bool(self.__buff)

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

