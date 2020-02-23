# pylint: disable=no-member

from actl.objects import Object
from actl.syntax import \
	SyntaxRules, CustomTemplate, IsInstance, Many, Or, Token, Maybe, Buffer
from actl.opcodes import \
	VARIABLE, SET_VARIABLE, CALL_FUNCTION, CALL_FUNCTION_STATIC


RULES = SyntaxRules()


def _hasAttr(attr):
	def rule(parser, token):
		scope = parser.scope

		if not isinstance(token, type(Object)):
			if not ((VARIABLE == token) and (token.name in scope)):
				return None
			token = scope[token.name]

		if not isinstance(token, type(Object)):
			return None

		return token.hasAttr(attr)

	return CustomTemplate.createToken(rule, f'_hasAttr({attr})')


def _runtimeRule(parser, inp):
	if not _hasAttr('__syntaxRule__')(parser, inp.copy()):
		return None

	syntaxRule = parser.scope[inp[0].name].getAttr('__syntaxRule__')
	return syntaxRule(parser, inp)


RULES.rawAdd(_runtimeRule)


@CustomTemplate.createToken
def _is_acceptable_name(_, token):
	return isinstance(token, str) and (token.isalpha() or token in ('_',))


@CustomTemplate.createToken
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


@RULES.add(IsInstance(VARIABLE), Token(' '), Token('='), manual_apply=True, use_parser=True)
def _(inp, parser):
	dst = inp.pop()
	assert inp.pop() == ' '
	assert inp.pop() == '='
	assert inp.pop() == ' '

	parsed, newInp = parser.parseUntil(inp, '\n')
	src = parsed.pop(-1)
	assert isinstance(src, VARIABLE)

	inp.set_(parsed + Buffer.of(SET_VARIABLE(dst.name, src.name)) + newInp)


@RULES.add(Or([Token('"')], [Token("'")]), manual_apply=True, use_parser=True)
def _(inp, parser):
	def _pop_start_token():
		start = [inp.pop()]
		if start != inp[0]:
			if start == inp[1]:
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
	inp.set_(Buffer.of(dst) + inp)


@CustomTemplate.createToken
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


@RULES.add(_hasAttr('__useCodeBlock__'), Token(':'), manual_apply=True, use_parser=True)
class UseCodeBlock:
	def __init__(self, parser, inp):
		var = inp.pop()
		assert inp.pop() == ':'
		code = self.popCodeBlock(parser, inp)

		var = var.getAttr('__useCodeBlock__').call(code)
		inp.set_(Buffer.of(var) + inp)

	@classmethod
	def popCodeBlock(cls, parser, inp):
		if inp[0] == '\n':
			code = cls._popFullCodeBlock(inp)
		else:
			code = cls._popInlineCodeBlock(inp)
		return parser.subParser(code)

	@classmethod
	def _popFullCodeBlock(cls, inp):
		code = Buffer()
		inp.pop()
		indent = cls._getFirstIndent(inp)

		while inp[:len(indent)] == indent:
			del inp[:len(indent)]
			while inp and (inp[0] != '\n'):
				code.append(inp.pop())
			if inp:
				code.append(inp.pop())

		return code

	@staticmethod
	def _getFirstIndent(inp):
		indent = ''

		for elem in inp:
			if elem not in (' ', '\t'):
				break
			indent += elem

		assert len(set(indent)) == 1
		return indent

	@staticmethod
	def _popInlineCodeBlock(inp):
		while inp[0] == ' ':
			inp.pop()

		code = Buffer()

		while inp and (inp[0] != '\n'):
			code.append(inp.pop(0))

		return code


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
