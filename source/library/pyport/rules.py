
from actl.parser import tokens
from actl.code import opcodes, Definition
from actl.syntax import SyntaxRules, Or, Maybe, Many, Range, Not


RULES = SyntaxRules()


@RULES.add(tokens.VARIABLE('pass'))
def _(_):
	return (opcodes.PASS,)


@RULES.add(tokens.VARIABLE('return'), tokens.VARIABLE, tokens.OPERATOR('line_end'))
def _(_, var, lend):
	return (opcodes.RETURN(var), lend)


@RULES.add(opcodes.BUILD_CODE, in_context=True, args=('code', 'idx_start'))
def _(code, idx_start):
	function = code.pop(idx_start).function
	result = code.create()
	if code and (code[idx_start] != tokens.OPERATOR('line_end')):
		while code and (code[idx_start] != tokens.OPERATOR('line_end')):
			result.append(code.pop(idx_start))
		function(result)
		return True
	code.pop(idx_start)
	indents = []
	while code and (tokens.INDENT == code[idx_start]):
		indents.append(code.pop(idx_start))
	result.extend(code.get_subcode(idx_start, code.index(tokens.OPERATOR('line_end'))+1))
	while True:
		for indent in indents:
			if (not code[idx_start:]) or (tokens.INDENT != code[idx_start]):
				function(result)
				return True
			assert indent == code[idx_start]
			code.pop(idx_start)
		result.extend(code.get_subcode(idx_start, code.index(tokens.OPERATOR('line_end'))+1))


@RULES.add(tokens.STRING, args=('code', 'idx_start', 'matched_code'))
def _(code, idx_start, matched_code):
	result = opcodes.BUILD_STRING(out=tokens.VARIABLE.get_temp(),
											string=matched_code[0].string)
	definition = code.create_definition((result,))
	return definition, result.out


@RULES.add(Range((tokens.OPERATOR('code_open'),), lambda _: (tokens.OPERATOR('code_close'),)),
			  args=('code', 'matched_code'))
def _(code, matched_code):
	subcode = code.create(matched_code[1:-1])
	return (subcode,)


@RULES.add(tokens.VARIABLE,
			  Range((Or(*((tokens.OPERATOR(bracket),) for bracket in tokens.OPERATOR.brackets)),),
					  lambda open_bracket: (open_bracket.mirror,)),
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
	out = tokens.VARIABLE.get_temp()
	definition.append(opcodes.CALL_FUNCTION(out=out,
														 function=function,
														 typeb=typeb,
														 args=cargs.args,
														 kwargs=cargs.kwargs))
	return definition, out


def build_cargs(code):
	result = opcodes.CARGS(args=[], kwargs=[])
	for opcode in code:
		if tokens.VARIABLE == opcode:
			result.args.append(opcode)
		elif tokens.OPERATOR(',') == opcode:
			continue
		else:
			raise RuntimeError(f'Unexpected opcode: {opcode}')
	return result


@RULES.add(tokens.VARIABLE, tokens.OPERATOR('='), tokens.VARIABLE,
			  in_context=True, args=('code', 'idx_start'))
def _(code, idx_start):
	out = code.pop(idx_start)
	code.pop(idx_start)
	subcode = code.get_subcode(idx_start, None)
	subcode.compile()
	source = subcode.pop(-1)
	code[idx_start:] = subcode
	code.insert(idx_start+len(subcode), opcodes.SET_VARIABLE(out=out, source=source))


@RULES.add(Many(tokens.VARIABLE,
					 Not(tokens.OPERATOR('=')),
					 Or(*((tokens.OPERATOR(symbol),) for symbol in tokens.OPERATOR.reloadable)),
					 tokens.VARIABLE),
			  Maybe(Not(tokens.OPERATOR('=')),
					  Or(*((tokens.OPERATOR(symbol),) for symbol in tokens.OPERATOR.reloadable)),
					  tokens.VARIABLE),
			  args=('code', 'matched_code'))
def _(code, matched_code):
	var1, operator, var2 = matched_code

	definition = code.create_definition()
	definition.append(opcodes.BUILD_STRING(out=tokens.VARIABLE.get_temp(),
														string=operator.operator))
	definition.append(opcodes.CALL_FUNCTION(out=tokens.VARIABLE.get_temp(),
														 function=tokens.VARIABLE('operator'),
														 typeb='(',
														 args=(definition[0].out,),
														 kwargs={}))
	definition.append(opcodes.CALL_FUNCTION(out=tokens.VARIABLE.get_temp(),
														 function=definition[1].out,
														 typeb='(',
														 args=(var1, var2),
														 kwargs={}))
	return definition, definition[2].out
