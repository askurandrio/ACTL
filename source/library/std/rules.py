
from actl.syntax import SyntaxRules, Template, CustomRule, IsInstance, Many, Or, Pdb, SimpleToken
from actl.code.opcodes import VARIABLE, END_LINE, SET_VARIABLE, BUILD_STRING


RULES = SyntaxRules()


_is_acceptable_name = CustomRule(
	'is_acceptable_name',
	lambda token: isinstance(token, str) and (token.isalpha() or token in ('_',))
)


@RULES.add(
	_is_acceptable_name,
	Many(
		Or(
			[_is_acceptable_name],
			[CustomRule(
				'is_acceptable_continues_name',
				lambda token: isinstance(token, str) and token.isdigit()
			)]
		),
		min_matches=0
	)
)
def _(*tokens):
	return [VARIABLE(''.join(tokens))]


@RULES.add(SimpleToken('\n'))
def _(token):
	return [END_LINE]


@RULES.add(
	IsInstance(VARIABLE),
	SimpleToken('='),
	IsInstance(VARIABLE),
	SimpleToken(END_LINE)
)
def _(src, _, dst, _1):
	return [SET_VARIABLE(src, dst), END_LINE]


@RULES.add(Or([SimpleToken('"')], [SimpleToken("'")]), manual_apply=True)
def _(inp, parser):
	def _pop_start_token():
		start = [inp.pop()]
		if start == inp.get():
			if start == inp.get(1):
				start.extend((inp.pop(), inp.pop()))
		return start
	
	start = _pop_start_token()
	out = ''
	while not inp.startswith(start):
		out += inp.pop()
	while start:
		assert start.pop(0) == inp.pop()
	dst = VARIABLE.temp()
	parser.define(BUILD_STRING(dst, out))
	inp[:0] = [dst]
	

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
