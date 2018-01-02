

from ...parser import Word, Operator
from ..SyntaxRule import SyntaxRule, SyntaxRules, Or
from .AnyOpCode import AnyOpCode


RULES = SyntaxRules()


class DynamicOpCode(AnyOpCode):
	_attributes = ()

	def __init__(self, *args, **kwargs):
		for key, value in zip(self._attributes, args):
			setattr(self, key, value)
		for key, value in kwargs.items():
			assert (not hasattr(self, key)), f'This attribute already exist: {key}, {self}'
			setattr(self, key, value)

	def __repr__(self):
		result = f'{self.__class__.__name__}('
		for key in self._attributes:
			result += f'{key}={getattr(self, key)}, '
		if result[-2:] == ', ':
			result = result[:-2]
		result += ')'
		return result

	@classmethod
	def create(cls, name, *attributes):
		code_template = 'class {name}(DynamicOpCode):\n' \
							 '   _attributes = ({attributes},)\n'
		code = code_template.format(name=name,
											 attributes=', '.join(f'"{attribute}"' for attribute in attributes))
		lc_scope = {'DynamicOpCode':cls}
		exec(code, globals(), lc_scope) #pylint: disable=W0122
		return lc_scope[name]


class Making(DynamicOpCode):
	_attributes = ('opcode',)

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False
		return self.opcode == other.opcode #pylint: disable=E1101


class VARIABLE(DynamicOpCode):
	__count_temp = 0
	_attributes = ('name',)

	@classmethod
	def get_temp(cls):
		cls.__count_temp += 1
		return cls(name=f'_R{cls.__count_temp}')


RULES.add(Word, lambda word: (VARIABLE(name=word.word),))

SET_VARIABLE = DynamicOpCode.create('SET_VARIABLE', 'destination', 'source')
RULES.add(VARIABLE, Operator('='), VARIABLE,
			 lambda destination, _, source: (SET_VARIABLE(destination, source),))

BUILD_TUPLE = DynamicOpCode.create('BUILD_TUPLE', 'variable', 'variables')


@RULES.add(Operator('('), None, in_context=True)
def _(code, idx_start, matched_code):
	count_braces = 0
	for idx_end, opcode in enumerate(code.buff[idx_start:], start=idx_start):
		if opcode == Operator('('):
			count_braces += 1
		if opcode == Operator(')'):
			count_braces -= 1
			if not count_braces:
				idx_end += 1
		if not count_braces:
			break
	subcode = code[idx_start:idx_end]
	del code[idx_start:idx_end]
	del subcode[0]
	del subcode[-1]
	subcode.compile()
	code.insert(idx_start, subcode[:-1])
	if subcode:
		code.insert(idx_start + 1, subcode[-1])


@RULES.add(Or((Making(BUILD_TUPLE),), (VARIABLE, Operator(','))), None, in_context=True)
def _(code, idx_start, matched_code): #pylint: disable=R1710
	if Making(BUILD_TUPLE) != matched_code[0]:
		code.insert(idx_start, Making(BUILD_TUPLE(variable=VARIABLE.get_temp(), variables=[])))
	result = code.buff[idx_start]
	idx_start += 1
	for idx_end, opcode in enumerate(code.buff[idx_start:], start=idx_start):
		if VARIABLE == opcode:
			result.opcode.variables.append(opcode)
		elif Operator(',') == opcode:
			continue
		else:
			del code[idx_start:idx_end]
			return Making
	code[idx_start-1] = result.opcode
	del code[idx_start:idx_end+1] #pylint: disable=W0631
