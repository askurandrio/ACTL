
from actl.code.opcodes import opcodes
from actl.code.Code import Definition
from actl.parser.opcodes import OPERATOR, STRING
from actl.syntax import SyntaxRules, Or, Maybe, Many, Range, Not

from ..operator import operator


RULES = SyntaxRules()


@RULES.add(STRING, args=('code', 'idx_start', 'matched_code'))
def _(code, idx_start, matched_code):
	result = opcodes.BUILD_STRING(out=opcodes.VARIABLE.get_temp(),
											string=matched_code[0].string)
	definition = code.create_definition((result,))
	return definition, result.out


@RULES.add(Range((OPERATOR('code_open'),), lambda _: (OPERATOR('code_close'),)),
			  args=('code', 'matched_code'))
def _(code, matched_code):
	subcode = code.create(matched_code[1:-1])
	return (subcode,)


@RULES.add(opcodes.VARIABLE,
			  Range((Or(*((OPERATOR(bracket),) for bracket in OPERATOR.brackets)),),
					  lambda open_bracket: (OPERATOR(OPERATOR.brackets[open_bracket.operator]),)),
			  args=('code', 'matched_code'))
def _(code, matched_code):
	function = matched_code[0]
	typeb = matched_code[1].operator
	subcode = code.create(list(matched_code[2:-1]))
	subcode.compile()
	if Definition == subcode.get(0):
		definition = subcode.pop(0)
	else:
		definition = code.create_definition()
	cargs = build_cargs(subcode)
	out = opcodes.VARIABLE.get_temp()
	definition.append(opcodes.CALL_FUNCTION(out=out,
														 function=function,
														 typeb=typeb,
														 args=cargs.args,
														 kwargs=cargs.kwargs))
	return definition, out


def build_cargs(code):
	result = opcodes.CARGS(args=[], kwargs=[])
	for opcode in code:
		if opcodes.VARIABLE == opcode:
			result.args.append(opcode)
		elif OPERATOR(',') == opcode:
			continue
		else:
			raise RuntimeError(f'Unexpected opcode: {opcode}')
	return result


@RULES.add(opcodes.VARIABLE, OPERATOR('='), opcodes.VARIABLE, OPERATOR('line_end'))
def _(var1, _, var2, line_end):
	return opcodes.SET_VARIABLE(var1, var2), line_end


@RULES.add(Many(opcodes.VARIABLE,
					 Not(OPERATOR('=')),
					 Or(*((OPERATOR(symbol),) for symbol in operator.allowed)),
					 opcodes.VARIABLE),
			  Maybe(Not(OPERATOR('=')),
					  Or(*((OPERATOR(symbol),) for symbol in operator.allowed)),
					  opcodes.VARIABLE),
			  args=('code', 'matched_code'))
def _(code, matched_code):
	var1, operator, var2 = matched_code
	operator = operator.operator

	from actl import Project

	out = opcodes.VARIABLE.get_temp()
	s_subcode = f'{out.name} = operator("{operator}")({var1.name}, {var2.name})'
	subcode = list(Project.this.parse(string=s_subcode))
	definition = code.create_definition(subcode)
	definition.compile()
	return definition, out
