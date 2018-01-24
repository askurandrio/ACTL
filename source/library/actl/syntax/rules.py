
import std
from ..parser.opcodes import OPERATOR, STRING
from ..code.opcodes import opcodes
from .SyntaxRule import SyntaxRules, Not, Or


def extract_code_from_brackets(code, idx_start):
	open_bracket = code[idx_start]
	close_brucket = OPERATOR(OPERATOR.brackets[open_bracket.operator])
	count_braces = 0
	for idx_end, opcode in enumerate(code[idx_start:], start=idx_start):
		if opcode == open_bracket:
			count_braces += 1
		elif opcode == close_brucket:
			count_braces -= 1
			if not count_braces:
				idx_end += 1
		if not count_braces:
			break
	assert not count_braces
	return code.get_subcode(idx_start, idx_end)


RULES = SyntaxRules()


@RULES.add(STRING, in_context=True)
def _(code, idx_start, _):
	result = opcodes.BUILD_STRING(out=opcodes.VARIABLE.get_temp(), string=code[idx_start].string)
	code[idx_start] = result.out
	code.add_definition(idx_start, (result,))


@RULES.add(OPERATOR('code_open'), in_context=True)
def _(code, idx_start, _):
	count_blocks = 0
	for idx_end, opcode in enumerate(code[idx_start:], start=idx_start):
		if OPERATOR('code_open') == opcode:
			count_blocks += 1
		elif OPERATOR('code_close') == opcode:
			count_blocks -= 1
			if not count_blocks:
				idx_end += 1
		if not count_blocks:
			break
	subcode = code.get_subcode(idx_start, idx_end)
	del subcode[0]
	del subcode[-1]
	code.insert(idx_start, subcode)


@RULES.add(Or(*((OPERATOR(bracket),) for bracket in OPERATOR.brackets)), in_context=True)
def _(code, idx_start, _, in_context=True):
	subcode = extract_code_from_brackets(code, idx_start)
	type_bracket = subcode[0].operator
	del subcode[0]
	del subcode[-1]

	if opcodes.VARIABLE == code.get(idx_start-1):
		ctuple = opcodes.Making(opcodes.CTUPLE(type=type_bracket, args=[], kwargs=[]))
		subcode.insert(0, ctuple)
	subcode.compile()
	code.insert(idx_start, subcode.pop(-1))
	code.add_definition(idx_start, subcode)


@RULES.add(opcodes.VARIABLE, OPERATOR(','))
def _(code, var, _):
	ctuple = opcodes.CTUPLE(out=opcodes.VARIABLE.get_temp(), type='(', args=[var], kwargs=[])
	return (opcodes.Making(ctuple),)


@RULES.add(opcodes.Making(opcodes.CTUPLE), in_context=True)
def _(code, idx_start, _): #pylint: disable=R1710
	result = code.buff[idx_start]
	idx_end = None
	for idx_end, opcode in enumerate(code.buff[idx_start:], start=idx_start):
		if (idx_end == idx_start) and opcode is result:
			continue
		elif opcodes.VARIABLE == opcode:
			result.opcode.args.append(opcode)
		elif OPERATOR(',') == opcode:
			continue
		else:
			del code[idx_start+1:idx_end]
			return opcodes.Making
	del code[idx_start:idx_end+1]
	code.insert(idx_start, result.opcode)


@RULES.add(opcodes.VARIABLE, opcodes.CTUPLE, in_context=True)
def _(code, idx_start, _):
	ctuple = code[idx_start+1]
	result = opcodes.CALL_FUNCTION(out=opcodes.VARIABLE.get_temp(),
											 function=code[idx_start],
											 type=ctuple.type,
											 args=ctuple.args,
											 kwargs=ctuple.kwargs)
	del code[idx_start+1]
	code[idx_start] = result.out
	code.add_definition(idx_start, (result,))



@RULES.add(opcodes.VARIABLE,
			  Or(*((OPERATOR(symbol),) for symbol in std.operator.allowed)),
			  opcodes.VARIABLE,
			  in_context=True)
def _(code, idx_start, idx_end):
	var1 = code.pop(idx_start)
	soperator = code.pop(idx_start).operator
	var2 = code.pop(idx_start)
	if soperator == '=':
		try:
			idx_end_line = code[idx_start:].index(OPERATOR('line_end'))
			idx_end_line += idx_start + 1
		except ValueError:
			idx_end_line = len(code)
		code.add_definition(idx_end_line, (opcodes.SET_VARIABLE(var1, var2),))
		code.insert(idx_start, var2)
	else:
		from actl import Project

		result = opcodes.VARIABLE.get_temp()
		code.insert(idx_start, result)

		s_subcode = f'{result.name} = operator("{soperator}")({var1.name}, {var2.name})'
		subcode = list(Project.this().parse(string=s_subcode))
		code.add_definition(idx_start, code.create(buff=subcode))
