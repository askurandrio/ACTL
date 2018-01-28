
from ..parser.opcodes import OPERATOR
from .opcodes import AnyOpCode
from .opcodes.opcodes import Making


class Code(AnyOpCode):
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
		is_add = False
		if Definition != self[idx]:
			self.insert(idx, self.create_definition())
			is_add = True
		self[idx].extend(opcodes)
		return is_add

	def compile(self):
		is_changed = False
		while self.__apply_rule():
			is_changed = True
		while self.__after_compile():
			is_changed = True
		return is_changed

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
				result_match = rule.match(self.buff[idx_start:])
				if result_match:
					result = rule(self, idx_start, result_match.idx_end)
					if rule.in_context:
						if result is Making:
							continue
					else:
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
			if Code == opcode:
				opcode.compile()
			#assert opcode in (Word, OPERATOR), f'{opcode} in {(Word, OPERATOR)}'

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

