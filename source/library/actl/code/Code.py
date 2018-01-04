
import weakref

from ..parser.opcodes import Operator
from .opcodes import AnyOpCode
from .opcodes.opcodes import Making
from .SyntaxRule import SyntaxRule


class Code(AnyOpCode):
	def __init__(self, buff, rules):
		self.buff = buff
		self.rules = rules

	def get(self, index, default=None):
		try:
			return self[index]
		except IndexError:
			return default

	def get_subcode(self, idx_start, idx_end):
		subcode = type(self)(self.buff[idx_start:idx_end], self.rules)
		del self[idx_start:idx_end]
		return subcode

	def insert(self, index, opcode):
		self.buff.insert(index, opcode)

	def extend(self, buff):
		self.buff.extend(buff)

	def compile(self):
		while self.__apply_rule():
			pass
		while self.__after_compile():
			pass

	def pop(self, index):
		return self.buff.pop(index)

	def add_definition(self, idx, opcodes):
		while (idx > 0) and (self[idx] != Operator('line_end')):
			idx -= 1
		if idx != 0:
			idx += 1
		is_add = False
		if Definition != self[idx]:
			self.insert(idx, Definition([], self.rules))
			is_add = True
		self[idx].extend(opcodes)
		return is_add

	def __apply_rule(self):
		for idx, _ in enumerate(self.buff):
			for rule in self.rules:
				idx_end = rule.match(self.buff[idx:])
				if idx_end is not None:
					result = rule(self, idx, self.buff[idx:idx+idx_end])
					if rule.in_context:
						if result is Making:
							continue
					else:
						self.buff[idx:idx+idx_end] = result
					return True

	def __after_compile(self):
		for idx, opcode in enumerate(self.buff):
			if Operator('line_end') == opcode:
				del self.buff[idx]
				return True
			#if type(self) == opcode:
			#	opcode.compile()
			#assert opcode in (Word, Operator), f'{opcode} in {(Word, Operator)}'

	def __iter__(self):
		return iter(self.buff)

	def __getitem__(self, index):
		buff = self.buff.__getitem__(index)
		if isinstance(index, slice):
			return type(self)(buff, self.rules)
		return buff

	def __setitem__(self, index, elem):
		self.buff.__setitem__(index, elem)

	def __delitem__(self, index):
		return self.buff.__delitem__(index)

	def __bool__(self):
		return bool(self.buff)

	def __repr__(self, is_lazy=False):
		if is_lazy:
			def generator():
				yield f'{type(self).__name__}:\n'
				for opcode in self:
					if isinstance(opcode, Code):
						for repr_opcode in opcode.__repr__(True):
							yield '   ' + repr_opcode
					else:
						yield '   ' + repr(opcode) + '\n'
			return generator()
		return ''.join(self.__repr__(True))


class Definition(Code):
	pass

