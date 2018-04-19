
import actl
from actl.tokenizer import tokens
from actl.code import opcodes, Definition
from actl.syntax import SyntaxRules, Or, Maybe, Many, Range, Not


RULES = SyntaxRules()


@RULES.add(tokens.VARIABLE('pass'))
def _(_):
	return (opcodes.PASS,)


@RULES.add(tokens.VARIABLE('return'), tokens.VARIABLE, tokens.OPERATOR('line_end'))
def _(_, var, lend):
	return (opcodes.RETURN(var), lend)


@RULES.add(tokens.VARIABLE, tokens.OPERATOR(':'),
			  in_context=True, args=('code', 'idx_start'))
def _(code, idx_start):
	function = code.pop(idx_start)

	code.pop(idx_start)
	code.pop(idx_start)

	indents = []
	while tokens.INDENT == code[idx_start]:
		indents.append(code.pop(idx_start))

	result = code.create()
	result.extend(code.extract(idx_start, code.index(tokens.OPERATOR('line_end'))+1))

	while True:
		for indent in indents:
			if indent == code.get(idx_start):
				code.pop(idx_start)
			else:
				code.insert(idx_start, opcodes.SAVE_CODE(function=function))
				code.insert(idx_start+1, result)
				return None
		result.extend(code.extract(idx_start, code.index(tokens.OPERATOR('line_end'))+1))
	code.insert(idx_start, opcodes.SAVE_CODE(function=function))
	code.insert(idx_start+1, result)
	return None


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
					  lambda open_bracket: (open_bracket.mirror,),
					  (Many(tokens.VARIABLE, tokens.OPERATOR(',')), Maybe(tokens.VARIABLE))),
			  args=('code', 'matched_code'))
def _(code, matched_code):
	call_function = matched_code.pop(0)
	call_typeb = matched_code.pop(0).operator
	matched_code.pop(-1)
	call_args = []
	it_matched_code = iter(matched_code)
	for opcode in it_matched_code:
		if tokens.VARIABLE == opcode:
			call_args.append(opcode)
			try:
				next(it_matched_code)
			except StopIteration:
				break

	definition = code.create_definition()
	definition.append(opcodes.CALL_FUNCTION(out=tokens.VARIABLE.get_temp(),
														 function=call_function,
														 typeb=call_typeb,
														 args=call_args,
														 kwargs={}))
	return definition, definition[0].out


@RULES.add(tokens.VARIABLE, tokens.OPERATOR('='), tokens.VARIABLE, tokens.OPERATOR('line_end'))
def _(out, _, source, line_end):
	result = opcodes.SET_VARIABLE(out=out, source=source)
	return result, line_end


@RULES.add(Many(tokens.VARIABLE,
					 Not(tokens.OPERATOR('=')),
					 Many(Or(*((tokens.OPERATOR(symbol),) for symbol in tokens.OPERATOR.reloadable))),
					 tokens.VARIABLE),
			  Maybe(Not(tokens.OPERATOR('=')),
					  Many(Or(*((tokens.OPERATOR(symbol),) for symbol in tokens.OPERATOR.reloadable))),
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
