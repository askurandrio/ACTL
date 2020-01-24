
from actl.syntax import \
	SyntaxRules, CustomTemplate, IsInstance, Many, Or, Token, Maybe, SyntaxRule
from actl.opcodes import \
	VARIABLE, END_LINE, SET_VARIABLE, CALL_FUNCTION, CALL_FUNCTION_STATIC


RULES = SyntaxRules()


def _runtimeRule(scope, inp):
	var = inp[0]

	if not (
		(VARIABLE == var) and
		(var.name in scope) and
		(scope[var.name].hasAttr('__syntaxRule__'))
	):
		return

	syntaxRule = scope[var.name].getAttr('__syntaxRule__')
	return syntaxRule(scope, inp)


RULES.rawAdd(_runtimeRule)


@CustomTemplate.create
def _is_acceptable_name(_, token):
	return isinstance(token, str) and (token.isalpha() or token in ('_',))


@CustomTemplate.create
def _is_acceptable_continues_name(_, token):
	return isinstance(token, str) and token.isdigit()


@RULES.add(
	_is_acceptable_name,
	Maybe(Many(
		Or(
			[_is_acceptable_name],
			[_is_acceptable_continues_name]
		)
	))
)
def _(*tokens):
	return [VARIABLE(''.join(tokens))]


@RULES.add(Token('\n'))
def _(_):
	return [END_LINE]


@RULES.add(
	IsInstance(VARIABLE),
	Token('='),
	IsInstance(VARIABLE),
	Token(END_LINE)
)
def _(src, _, dst, _1):
	return [SET_VARIABLE(src, dst), END_LINE]


@RULES.add(Or([Token('"')], [Token("'")]), manual_apply=True, use_parser=True)
def _(inp, parser):
	def _pop_start_token():
		start = [inp.pop()]
		if start == inp.get():
			if start == inp.get(1):
				start.extend((inp.pop(), inp.pop()))
		return start

	start = _pop_start_token()
	string = ''
	while not inp.startswith(start):
		string += inp.pop()
	while start:
		assert start.pop(0) == inp.pop()
	dst = VARIABLE.temp()
	parser.define(CALL_FUNCTION_STATIC(dst=dst.name, function='String', typeb='(', args=[string]))
	inp[:0] = [dst]


@CustomTemplate.create
def _is_digit(_, token):
	return isinstance(token, str) and token.isdigit()


@RULES.add(Many(_is_digit), Maybe(Token('.'), Many(_is_digit)), use_parser=True)
def _(*args, parser=None):
	number = ''.join(args)
	dst = VARIABLE.temp()
	parser.define(CALL_FUNCTION_STATIC(dst=dst.name, function='Number', typeb='(', args=[number]))
	return [dst]


@RULES.add(
	IsInstance(VARIABLE),
	Token('('),
	Maybe(Many(IsInstance(VARIABLE), min_matches=1)),
	Token(')'),
	use_parser=True
)
def _(function, op_token, *args, parser=None):
	args = [arg.name for arg in args[:-1]]
	dst = VARIABLE.temp()
	parser.define(CALL_FUNCTION(dst.name, function.name, op_token, args, {}))
	return [dst]


#
# @RULES.add(tokens.VARIABLE('pass'))
# def _(buff):
# 	buff.pop()
# 	yield opcodes.PASS
#
#
# @RULES.add(tokens.NUMBER)
# def _(buff):
# 	number = buff.pop().number
# 	if (tokens.OPERATOR(',') == buff.get(0)) and (tokens.NUMBER == buff.get(1)):
# 		buff.pop()
# 		number += f'.{buff.pop().number}'
# 	dst = tokens.VARIABLE.get_temp()
# 	yield Definition(opcodes.BUILD_NUMBER(dst=dst, number=number))
# 	yield dst
#
#
# @RULES.add(tokens.VARIABLE('return'), tokens.VARIABLE, tokens.OPERATOR('line_end'))
# def _(buff):
# 	buff.pop()
# 	yield opcodes.RETURN(buff.pop())
#
#
# @RULES.add(tokens.VARIABLE, tokens.OPERATOR(':'))
# def _(buff):
# 	yield opcodes.SAVE_CODE(function=buff.pop())
# 	buff.shift(1)
#
# 	buff.pop()
# 	buff.pop()
#
# 	yield_indents = []
# 	while True:
# 		indent = buff.pop()
# 		if tokens.INDENT != buff.get(0):
# 			remove_indent = indent
# 			break
# 		yield_indents.append(indent)
# 		yield indent
#
# 	code = Code()
# 	while buff:
# 		code.append(buff.pop())
# 		if tokens.OPERATOR('line_end') == code[-1]:
# 			break
#
# 	while buff:
# 		for indent in yield_indents:
# 			if indent == buff.get(0):
# 				yield buff.pop()
# 			else:
# 				yield code
# 				return None
# 		if remove_indent == buff.get(0):
# 			buff.pop()
# 		else:
# 			yield code
# 			return None
#
# 		while buff:
# 			code.append(buff.pop())
# 			if tokens.OPERATOR('line_end') == code[-1]:
# 				break
# 	yield code
# 	return None
#
#
# @RULES.add(tokens.STRING)
# def _(buff):
# 	dst = tokens.VARIABLE.get_temp()
# 	yield Definition(opcodes.BUILD_STRING(dst=dst, string=buff.pop().string))
# 	yield dst
#
#
# @RULES.add(tokens.OPERATOR('code_open'))
# def build_code(buff):
# 	buff.pop()
# 	code = Code()
# 	while True:
# 		if tokens.OPERATOR('code_open') == buff[0]:
# 			code.extend(build_code(buff))
# 		elif tokens.OPERATOR('code_close') == buff[0]:
# 			buff.pop()
# 			break
# 		else:
# 			code.append(buff.pop())
# 	yield code
#
#
# @RULES.add(tokens.VARIABLE,
# 			  Or(*((brackets[0],) for brackets in tokens.OPERATOR.get_brackets())))
# def _(buff):
# 	call_function = buff.pop()
# 	call_typeb = buff.pop().operator
# 	close_bracket_op = tokens.OPERATOR(call_typeb).get_mirror()
# 	call_args = []
# 	while True:
# 		if tokens.VARIABLE == buff[0]:
# 			call_args.append(buff.pop())
# 			if tokens.OPERATOR(',') == buff[0]:
# 				buff.pop()
# 		elif close_bracket_op == buff[0]:
# 			buff.pop()
# 			break
# 		else:
# 			raise RuntimeError(buff[0])
#
# 	dst = tokens.VARIABLE.get_temp()
# 	yield Definition(opcodes.CALL_FUNCTION(dst=dst,
# 														function=call_function,
# 														typeb=call_typeb,
# 														args=call_args,
# 														kwargs={}))
# 	yield dst
#
#
# @RULES.add(Or(*((brackets[0],) for brackets in tokens.OPERATOR.get_brackets())))
# def _(buff):
# 	open_bracket = buff.pop()
# 	close_bracket = open_bracket.get_mirror()
# 	count = 1
# 	code = Code()
# 	while count:
# 		if open_bracket == buff[0]:
# 			count += 1
# 			code.append(buff.pop())
# 		elif close_bracket == buff[0]:
# 			count -= 1
# 			buff.pop()
# 		else:
# 			code.append(buff.pop())
# 	yield Command('compile', code)
# 	yield code.pop(-1)
#
#
# @RULES.add(tokens.VARIABLE, tokens.OPERATOR('='), tokens.VARIABLE, tokens.OPERATOR('line_end'))
# def _(buff):
# 	dst = buff.pop()
# 	buff.pop()
# 	src = buff.pop()
# 	yield opcodes.SET_VARIABLE(dst=dst, src=src)
#
#
# TMPL_OPERATORS = Many(Or(*((operator,) for operator in tokens.OPERATOR.get_reloadable())))
# @RULES.add(Many(tokens.VARIABLE, Not(tokens.OPERATOR('=')), TMPL_OPERATORS, tokens.VARIABLE))
# def _(buff):
# 	args = []
# 	args.append(buff.pop())
# 	while buff:
# 		operator = ''
# 		while buff[0] in tokens.OPERATOR.get_reloadable():
# 			operator += buff.pop().operator
# 		args.append(buff.pop())
# 		dst = tokens.VARIABLE.get_temp()
# 		yield Definition(opcodes.CALL_OPERATOR(dst=dst, operator=operator, args=args))
# 		if buff.get(0) in tokens.OPERATOR.get_reloadable():
# 			args = []
# 			args.append(dst)
# 	yield dst
