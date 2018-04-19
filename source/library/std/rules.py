
import actl
from actl.tokenizer import tokens
from actl.code import opcodes, Definition
from actl.syntax import SyntaxRules, Or, Maybe, Many, Range, Not


RULES = SyntaxRules()


@RULES.add(tokens.VARIABLE('pass'))
def _(_):
	return (opcodes.PASS,)


@RULES.add(Or((tokens.NUMBER, tokens.OPERATOR('.'), tokens.NUMBER), (tokens.NUMBER,)))
def _(num1, *other):
	definition = Definition()
	if other:
		number = f'{num1.number}.{other[1].number}'
	else:
		number = num1.number		
	definition.append(opcodes.BUILD_NUMBER(dst=tokens.VARIABLE.get_temp(), number=number))
	return definition, definition[0].dst


@RULES.add(tokens.VARIABLE('return'), tokens.VARIABLE, tokens.OPERATOR('line_end'))
def _(_, var, line_end):
	return opcodes.RETURN(var), line_end


@RULES.add(tokens.VARIABLE, tokens.OPERATOR(':'),
			  in_context=True, args=('code', 'idx_start'))
def _(code, idx_start):
	function = code.pop(idx_start)

	code.pop(idx_start)
	code.pop(idx_start)

	indents = []
	while tokens.INDENT == code[idx_start]:
		indents.append(code.pop(idx_start))

	result = type(code)(buff=[], scope=code.scope)
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


@RULES.add(tokens.STRING)
def _(token):
	definition = Definition()
	definition.append(opcodes.BUILD_STRING(dst=tokens.VARIABLE.get_temp(),
														string=token.string))
	return definition, definition[-1].dst


@RULES.add(Range((tokens.OPERATOR('code_open'),), lambda _: (tokens.OPERATOR('code_close'),)),
			args=('code', 'matched_code'))
def _(code, matched_code):
	return (type(code)(buff=matched_code[1:-1], scope=code.scope),)


@RULES.add(tokens.VARIABLE, 
			  Range((Or(*((tokens.OPERATOR(bracket),) for bracket in tokens.OPERATOR.brackets)),),
					  lambda open_bracket: (open_bracket.mirror,),
					  (Maybe(Many(tokens.VARIABLE, tokens.OPERATOR(',')), Maybe(tokens.VARIABLE)),)))
def _(*matched_code):
	matched_code = list(matched_code)
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

	definition = Definition()
	definition.append(opcodes.CALL_FUNCTION(dst=tokens.VARIABLE.get_temp(),
														 function=call_function,
														 typeb=call_typeb,
														 args=call_args,
														 kwargs={}))
	return definition, definition[0].dst


@RULES.add(tokens.OPERATOR('('), tokens.VARIABLE, tokens.OPERATOR(')'))
def _(_op1, var, _op2):
	return (var,)


@RULES.add(tokens.VARIABLE, tokens.OPERATOR('='), tokens.VARIABLE, tokens.OPERATOR('line_end'))
def _(dst, _, source, line_end):
	result = opcodes.SET_VARIABLE(dst=dst, source=source)
	return result, line_end


TMPL_OPERATORS = Many(Or(*((tokens.OPERATOR(symbol),) for symbol in tokens.OPERATOR.reloadable)))
@RULES.add(Many(tokens.VARIABLE, Not(tokens.OPERATOR('=')), TMPL_OPERATORS, tokens.VARIABLE))
def _(*matched_code_ungroup):
	matched_code_ungroup = list(matched_code_ungroup)
	matched_code = []
	while matched_code_ungroup:
		if tokens.VARIABLE == matched_code_ungroup[0]:
			matched_code.append(matched_code_ungroup.pop(0))
		elif tokens.OPERATOR == matched_code_ungroup[0]:
			operator = ''
			while matched_code_ungroup and (tokens.OPERATOR == matched_code_ungroup[0]):
				operator += matched_code_ungroup.pop(0).operator
			matched_code.append(operator)
		else:
			raise RuntimeError(matched_code_ungroup)
	definition = Definition()

	if tokens.OPERATOR == matched_code[0]:
		definition.append(opcodes.CALL_OPERATOR(dst=tokens.VARIABLE.get_temp(),
															 operator=matched_code.pop(0),
															 args=[matched_code.pop(0)]))
		matched_code.insert(0, definition[-1].dst)

	while (len(matched_code) >= 3) and \
				(tokens.VARIABLE == matched_code[0]) and \
				(tokens.VARIABLE == matched_code[2]):
		args = []
		args.append(matched_code.pop(0))
		operator = matched_code.pop(0)
		args.append(matched_code.pop(0))
		definition.append(opcodes.CALL_OPERATOR(dst=tokens.VARIABLE.get_temp(),
															 operator=operator,
															 args=args))
		matched_code.insert(0, definition[-1].dst)

	if len(matched_code) == 2:
		args = [matched_code.pop(0)]
		definition.append(opcodes.CALL_OPERATOR(dst=tokens.VARIABLE.get_temp(),
															 operator=matched_code.pop(0),
															 args=args))
		matched_code.insert(0, definition[-1].dst)

	return definition, matched_code.pop(0)
