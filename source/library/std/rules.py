
from actl.tokenizer import tokens
from actl.code import opcodes, Code, Definition
from actl.syntax import SyntaxRules, Command, Or, Maybe, Many, Range, Not


RULES = SyntaxRules()


@RULES.add(tokens.VARIABLE('pass'))
def _(buff):
	buff.pop(0)
	yield opcodes.PASS


@RULES.add(tokens.NUMBER)
def _(buff):
	number = buff.pop(0).number
	if (tokens.OPERATOR(',') == buff.get(0)) and (tokens.NUMBER == buff.get(1)):
		buff.pop(0)
		number += f'.{buff.pop(0).number}'
	dst = tokens.VARIABLE.get_temp()
	yield Definition(opcodes.BUILD_NUMBER(dst=dst, number=number))
	yield dst


@RULES.add(tokens.VARIABLE('return'), tokens.VARIABLE, tokens.OPERATOR('line_end'))
def _(buff):
	buff.pop(0)
	yield opcodes.RETURN(buff.pop(0))


@RULES.add(tokens.VARIABLE, tokens.OPERATOR(':'))
def _(buff):
	yield opcodes.SAVE_CODE(function=buff.pop(0))
	buff.shift(1)

	buff.pop(0)
	buff.pop(0)

	yield_indents = []
	while True:
		indent = buff.pop(0)
		if tokens.INDENT != buff.get(0):
			remove_indent = indent
			break
		yield_indents.append(indent)
		yield indent

	code = Code()
	while buff:
		code.append(buff.pop(0))
		if tokens.OPERATOR('line_end') == code[-1]:
			break

	while buff:
		for indent in yield_indents:
			if indent == buff.get(0):
				yield buff.pop(0)
			else:
				yield code
				return None
		if remove_indent == buff.get(0):
			buff.pop(0)
		else:
			yield code
			return None

		while buff:
			code.append(buff.pop(0))
			if tokens.OPERATOR('line_end') == code[-1]:
				break
	yield code
	return None


@RULES.add(tokens.STRING)
def _(buff):
	dst = tokens.VARIABLE.get_temp()
	yield Definition(opcodes.BUILD_STRING(dst=dst, string=buff.pop(0).string))
	yield dst


@RULES.add(tokens.OPERATOR('code_open'))
def build_code(buff):
	buff.pop(0)
	code = Code()
	while True:
		if tokens.OPERATOR('code_open') == buff[0]:
			code.extend(build_code(buff))
		elif tokens.OPERATOR('code_close') == buff[0]:
			buff.pop(0)
			break
		else:
			code.append(buff.pop(0))
	yield code


@RULES.add(tokens.VARIABLE,
			  Or(*((brackets[0],) for brackets in tokens.OPERATOR.get_brackets())))
def _(buff):
	call_function = buff.pop(0)
	call_typeb = buff.pop(0).operator
	close_bracket_op = tokens.OPERATOR(call_typeb).get_mirror()
	call_args = []
	while True:
		if tokens.VARIABLE == buff[0]:
			call_args.append(buff.pop(0))
			if tokens.OPERATOR(',') == buff[0]:
				buff.pop(0)
		elif close_bracket_op == buff[0]:
			buff.pop(0)
			break
		else:
			raise RuntimeError(buff[0])

	dst = tokens.VARIABLE.get_temp()
	yield Definition(opcodes.CALL_FUNCTION(dst=dst,
														function=call_function,
														typeb=call_typeb,
														args=call_args,
														kwargs={}))
	yield dst


@RULES.add(Or(*((brackets[0],) for brackets in tokens.OPERATOR.get_brackets())))
def _(buff):
	open_bracket = buff.pop(0)
	close_bracket = open_bracket.get_mirror()
	count = 1
	code = Code()
	while count:
		if open_bracket == buff[0]:
			count += 1
			code.append(buff.pop(0))
		elif close_bracket == buff[0]:
			count -= 1
			buff.pop(0)
		else:
			code.append(buff.pop(0))
	yield Command('compile', code)
	yield code.pop(-1)


@RULES.add(tokens.VARIABLE, tokens.OPERATOR('='), tokens.VARIABLE, tokens.OPERATOR('line_end'))
def _(buff):
	dst = buff.pop(0)
	buff.pop(0)
	src = buff.pop(0)
	yield opcodes.SET_VARIABLE(dst=dst, src=src)


TMPL_OPERATORS = Many(Or(*((operator,) for operator in tokens.OPERATOR.get_reloadable())))
@RULES.add(Many(tokens.VARIABLE, Not(tokens.OPERATOR('=')), TMPL_OPERATORS, tokens.VARIABLE))
def _(buff):
	args = []
	args.append(buff.pop(0))
	while buff:
		operator = ''
		while buff[0] in tokens.OPERATOR.get_reloadable():
			operator += buff.pop(0).operator
		args.append(buff.pop(0))
		dst = tokens.VARIABLE.get_temp()
		yield Definition(opcodes.CALL_OPERATOR(dst=dst, operator=operator, args=args))
		if buff.get(0) in tokens.OPERATOR.get_reloadable():
			args = []
			args.append(dst)
	yield dst
