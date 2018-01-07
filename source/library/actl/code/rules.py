
import std
from ..parser import Word, OPERATOR
from .opcodes import opcodes
from .SyntaxRule import SyntaxRules, Not, Or


RULES = SyntaxRules()


@RULES.add(Word)
def _(_, word):
	return (opcodes.VARIABLE(name=word.word),)


@RULES.add(Or(*((OPERATOR(bracket),) for bracket in OPERATOR.brackets)), in_context=True)
def _(code, idx_start, _):
	open_bracket = code[idx_start]
	close_brucket = OPERATOR(OPERATOR.brackets[open_bracket.operator])
	next_code = code[idx_start+1:]
	next_code.compile()
	code.buff[idx_start+1:] = next_code.buff

	count_braces = 0
	for idx_end, opcode in enumerate(code.buff[idx_start:], start=idx_start):
		if opcode == open_bracket:
			count_braces += 1
		if opcode == close_brucket:
			count_braces -= 1
			if not count_braces:
				idx_end += 1
		if not count_braces:
			break
	assert not count_braces
	subcode = code.get_subcode(idx_start, idx_end)
	code.insert(idx_start, opcodes.BRACKETS(subcode[0].operator))
	del subcode[0]
	del subcode[-1]
	subcode.compile()
	code.insert(idx_start+1, subcode.pop(-1))
	code.add_definition(idx_start, subcode)


@RULES.add(Or((opcodes.Making(opcodes.BUILD_CTUPLE),), (opcodes.VARIABLE, OPERATOR(','))),
				in_context=True)
def _(code, idx_start, _): #pylint: disable=R1710
	if opcodes.VARIABLE == code[idx_start]:
		opcode = opcodes.BUILD_CTUPLE(out=opcodes.VARIABLE.get_temp(), args=[], kwargs={})
		code.insert(idx_start, opcodes.Making(opcode))
	result = code.buff[idx_start]
	idx_end = idx_start
	for idx_end, opcode in enumerate(code.buff[idx_start:], start=idx_start):
		if (idx_end == idx_start) and opcode is result:
			continue
		elif (opcodes.VARIABLE == opcode) and (code.get(idx_end+1, OPERATOR(',')) == OPERATOR(',')):
			result.opcode.args.append(opcode)
		elif OPERATOR(',') == opcode:
			continue
		else:
			del code[idx_start+1:idx_end]
			return opcodes.Making
	code[idx_start] = result.opcode.out
	del code[idx_start+1:idx_end+1]
	code.add_definition(idx_start, (result.opcode,))


@RULES.add(opcodes.VARIABLE,
			  Or(*((opcodes.BRACKETS(bracket),) for bracket in OPERATOR.brackets)), 
			  opcodes.VARIABLE,
			  in_context=True)
def _(code, idx_start, _):
	result = opcodes.CALL_FUNCTION(out=opcodes.VARIABLE.get_temp(),
											 function=code[idx_start],
											 type=code[idx_start+1].bracket,
											 ctuple=code[idx_start+2])
	code[idx_start] = result.out
	del code[idx_start+1:idx_start+3]
	code.add_definition(idx_start, (result,))


@RULES.add(Not((opcodes.VARIABLE,),
					(Or(*((opcodes.BRACKETS(bracket),) for bracket in OPERATOR.brackets)),)), 
			  opcodes.VARIABLE,
			  in_context=True)
def _(code, idx_start, _):
	functions = {'(':'tuple', '[':'list', '{':'dict', '<':'template'}
	function = opcodes.VARIABLE(functions[code[idx_start].bracket])
	out = opcodes.VARIABLE.get_temp()
	code[idx_start] = out
	call_code = opcodes.CALL_FUNCTION.build(out, function,
														 kwargs={'ctuple':code[idx_start+1]})
	del code[idx_start+1]
	code.add_definition(idx_start, call_code)


@RULES.add(opcodes.VARIABLE,
			  Or(*((OPERATOR(symbol),) for symbol in std.operator.allowed)),
			  opcodes.VARIABLE,
			  in_context=True)
def _(code, idx_start, idx_end):
	var1 = code.pop(idx_start)
	soperator = code.pop(idx_start).operator
	var2 = code.pop(idx_start)
	if soperator == '=':
		code.insert(idx_start, opcodes.SET_VARIABLE(var1, var2))
	else:
		var_soperator, operator, result = opcodes.VARIABLE.get_temp(3)
		subcode = code.create()
		subcode.append(opcodes.BUILD_STRING(var_soperator, soperator))
		subcode.extend(opcodes.CALL_FUNCTION.build(operator, opcodes.VARIABLE('operator'),
																 args=[var_soperator]))
		subcode.extend(opcodes.CALL_FUNCTION.build(result, operator,
																 args=[var1, var2]))
		subcode.compile()
		code.insert(idx_start, result)
		code.add_definition(idx_start, subcode)
