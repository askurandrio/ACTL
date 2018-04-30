
import sys
import copy

import pyparsing

from ..code.opcodes.AnyOpCode import MetaAnyOpCode, AnyOpCode, DynamicOpCode


ALPHAS = ''.join(filter(str.isalpha, map(chr, range(sys.maxunicode + 1))))


class INDENT(DynamicOpCode):
	__slots__ = ('string',)
	__hash__ = AnyOpCode.__hash__

	def __eq__(self, other):
		if not super().__eq__(other):
			return False
		return self.string == other.string


class VARIABLE(DynamicOpCode):
	__count_temp = 10
	__slots__ = ('name',)
	__hash__ = AnyOpCode.__hash__

	def __eq__(self, other):
		if not super().__eq__(other):
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
		if not super().__eq__(other):
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
	def __init__(cls, *args, **kwargs):
		cls.__operators = {}
		for operator in ':.+-!=*/@<>(){}[],;':
			cls.__build(operator)
		cls.__build('line_end')
		cls.__build('code_open')
		cls.__build('code_close')
		super().__init__(*args, **kwargs)

	def __build(cls, operator):
		cls.__operators[operator] = super().__call__(operator)

	def __call__(cls, operator):
		return cls.__operators[operator]


class OPERATOR(AnyOpCode, metaclass=MetaOPERATOR):
	__hash__ = AnyOpCode.__hash__

	def __init__(self, operator):
		self.operator = operator

	def get_mirror(self):
		for open_bracket, close_bracket in self.get_brackets():
			if self == open_bracket:
				return close_bracket
			if self == close_bracket:
				return open_bracket
		raise RuntimeError(f'Mirror not found: {self}')

	def __eq__(self, item):
		return self is item

	def __repr__(self):
		return f'OPERATOR("{self.operator}")'

	@classmethod
	def get_reloadable(cls):
		for operator in ':.+-!=*/<>':
			yield cls(operator)

	@classmethod
	def get_brackets(cls):
		yield cls('<'), cls('>')
		yield cls('['), cls(']')
		yield cls('{'), cls('}')
		yield cls('('), cls(')')

	@classmethod
	def get_toperators(cls):
		yield from cls.get_reloadable()
		for brackets in cls.get_brackets():
			yield from brackets
		yield cls(',')
		yield cls(';')

	@classmethod
	def get_tokenizers(cls):
		parser = pyparsing.LineEnd()
		parser.setParseAction(lambda _: cls('line_end'))
		yield parser

		for operator in cls.get_toperators():
			parser = pyparsing.Literal(operator.operator)
			parser.setParseAction(lambda tokens: cls(tokens[0]))
			yield parser
