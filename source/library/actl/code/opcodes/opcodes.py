

from ...parser import Word, OPERATOR
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
		return cls(name=f'__IV{cls.__count_temp}')


RULES.add(Word, lambda word: (VARIABLE(name=word.word),))

SET_VARIABLE = DynamicOpCode.create('SET_VARIABLE', 'dest', 'source')
RULES.add(VARIABLE, OPERATOR('='), VARIABLE,
			 lambda dest, _, source: (SET_VARIABLE(dest, source),))

SET_TYPE_CTUPLE = DynamicOpCode.create('SET_TYPE_CTUPLE', 'bracket')
BUILD_CTUPLE = DynamicOpCode.create('BUILD_CTUPLE', 'out', 'type', 'args', 'kwargs')
CALL_FUNCTION = DynamicOpCode.create('CALL_FUNCTION', 'out', 'function', 'ctuple')


@RULES.add(Or(*((OPERATOR(bracket),) for bracket in OPERATOR.brackets)), None, in_context=True)
def _(code, idx_start, matched_code):
	open_bracket = matched_code[0]
	close_brucket = OPERATOR(OPERATOR.brackets[open_bracket.operator])
	count_braces = 0
	idx_end = idx_start
	for idx_end, opcode in enumerate(code.buff[idx_start:], start=idx_start):
		if opcode == open_bracket:
			count_braces += 1
		if opcode == close_brucket:
			count_braces -= 1
			if not count_braces:
				idx_end += 1
		if not count_braces:
			break
	subcode = code.get_subcode(idx_start, idx_end)
	subcode[0] = SET_TYPE_CTUPLE(subcode[0].operator)
	del subcode[-1]
	subcode.compile()
	definitions = []
	definitions.append(subcode[:-1])
	#create CALL_FUNCTION opcode(if needed)
	if code[:idx_start] and (VARIABLE == code[idx_start - 1]):
		call_function = CALL_FUNCTION(out=VARIABLE.get_temp(),
												function=code[idx_start - 1],
												ctuple=subcode.pop(-1))
		definitions.append(call_function)
		code[idx_start-1:idx_start+1] = (call_function.out,)
	else:
		code[idx_start] = subcode.pop(-1)
	code.add_definition(idx_start, definitions)	


@RULES.add(Or((Making(BUILD_CTUPLE),), (VARIABLE, OPERATOR(',')), (SET_TYPE_CTUPLE,)),
			  None, in_context=True)
def _(code, idx_start, matched_code): #pylint: disable=R1710
	if Making(BUILD_CTUPLE) == matched_code[0]:
		pass
	elif VARIABLE == matched_code[0]:
		opcode = BUILD_CTUPLE(out=VARIABLE.get_temp(), type='(', args=[], kwargs=[])
		code.insert(idx_start, Making(opcode))
	elif SET_TYPE_CTUPLE == matched_code[0]:
		opcode = BUILD_CTUPLE(out=VARIABLE.get_temp(), type=matched_code[0].bracket, args=[], kwargs=[])
		code[idx_start] = Making(opcode)
	result = code.buff[idx_start]
	idx_end = idx_start
	for idx_end, opcode in enumerate(code.buff[idx_start:], start=idx_start):
		if (idx_end == idx_start) and opcode is result:
			continue
		elif (VARIABLE == opcode) and (code.get(idx_end+1, OPERATOR(',')) == OPERATOR(',')):
			result.opcode.args.append(opcode)
		elif OPERATOR(',') == opcode:
			continue
		elif SET_VARIABLE == opcode:
			result.opcode.kwargs.append(opcode)
		else:
			del code[idx_start+1:idx_end]
			return Making
	if code.add_definition(idx_start, (result.opcode,)):
		idx_start += 1
		idx_end += 1
	code[idx_start] = result.opcode.out
	del code[idx_start+1:idx_end+1]


@RULES.add(Making(CALL_FUNCTION), VARIABLE, None, in_context=True)
def _(code, idx_start, matched_code):
	opcode = matched_code[0].opcode
	opcode.ctuple = code.pop(idx_start+1)
	if code.add_definition(idx_start, (opcode,)):
		idx_start += 1
	code[idx_start] = opcode.out


#RULES.add(VARIABLE,
#			  Or(*((OPERATOR(symbol),) for symbol in OPERATOR.symbols)),
#			  VARIABLE,
#			  None,
#			  in_context=True)
def _(code, idx_start, matched_code): #pylint: disable=R1710
	print(code[idx_start:])
	raise 1
