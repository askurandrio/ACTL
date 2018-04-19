
import sys

import pyparsing

from ..code.opcodes.AnyOpCode import MetaAnyOpCode, AnyOpCode, DynamicOpCode


ALPHAS = ''.join(filter(str.isalpha, map(chr, range(sys.maxunicode + 1))))


class INDENT(DynamicOpCode):
	__slots__ = ('string',)
	__hash__ = AnyOpCode.__hash__

	def __eq__(self, other):
		if super().__eq__(other):
			return self.string == other.string


class VARIABLE(DynamicOpCode):
	__count_temp = 10
	__slots__ = ('name',)
	__hash__ = AnyOpCode.__hash__

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False
		return self.name == other.name #pylint: disable=E1101

	@classmethod
	def get_temp(cls, count=None):
		if count is not None:
			return [cls.get_temp() for _ in range(count)]
		cls.__count_temp += 1
		return cls(name=f'__IV{cls.__count_temp}')

	@classmethod
	def get_tokenizers(cls):
		word = pyparsing.Word(ALPHAS, ALPHAS + '_' + pyparsing.nums)
		word.setParseAction(lambda tokens: cls(tokens[0]))
		yield word


class NUMBER(DynamicOpCode):
	__slots__ = ('number',)
	__hash__ = AnyOpCode.__hash__

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False
		return self.number == other.number #pylint: disable=E1101

	@classmethod
	def get_tokenizers(cls):
		word = pyparsing.Word(pyparsing.nums)
		word.setParseAction(lambda tokens: cls(tokens[0]))
		yield word


class STRING(AnyOpCode):
	__hash__ = AnyOpCode.__hash__

	def __init__(self, string):
		self.string = string

	def __eq__(self, other):
		if super().__eq__(other):
			return self.string == other.string

	def __repr__(self):
		return f'{type(self)}("{self.string}")'

	@classmethod
	def get_tokenizers(cls):
		parser = pyparsing.QuotedString(quoteChar='"')
		parser.setParseAction(lambda tokens: cls(tokens[0]))
		yield parser


class MetaOPERATOR(MetaAnyOpCode):
	def __init__(self, *args, **kwargs):
		self.__cache = {}
		super().__init__(*args, **kwargs)

	def __call__(self, operator):
		try:
			return self.__cache[operator]
		except KeyError:
			self.__cache[operator] = super().__call__(operator)
			return self(operator)


class OPERATOR(AnyOpCode, metaclass=MetaOPERATOR):
	__hash__ = AnyOpCode.__hash__
	reloadable = ':.+-!=*/<>@' 
	brackets = {'(':')', '{':'}', '[':']', '<':'>'}
	symbols = reloadable + ',;' + ''.join(f'{item[0]}{item[1]}' for item in brackets.items())
	allowed = set(tuple(symbols) + (None, 'line_end', 'code_open', 'code_close'))

	def __init__(self, operator):
		if operator == '\n':
			operator = 'line_end'
		assert operator in self.allowed
		self.operator = operator

	@property
	def mirror(self):
		if self.operator in self.brackets.keys():
			return type(self)(self.brackets[self.operator])
		elif self.operator in self.brackets.values():
			for key, value in self.brackets.values():
				if value == self.operator:
					return type(self)(key)
		raise RuntimeError(f'Mirror not found: {self}')

	def __eq__(self, item):
		return self is item

	def __repr__(self):
		return f'OPERATOR("{self.operator}")'
	
	@classmethod
	def get_tokenizers(cls):
		parser = pyparsing.LineEnd()
		parser.setParseAction(lambda _: cls('line_end'))
		yield parser
		
		for symbol in cls.symbols:
			parser = pyparsing.Literal(symbol)
			parser.setParseAction(lambda tokens: cls(tokens[0]))
			yield parser
