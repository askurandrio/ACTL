# pylint: disable=no-member

from actl.objects import String, Number, Object
from actl.syntax import SyntaxRules, CustomTemplate, IsInstance, Many, Or, Token, Maybe, Buffer, \
	Template, BufferRule
from actl.opcodes import VARIABLE, SET_VARIABLE, CALL_FUNCTION, CALL_FUNCTION_STATIC, CALL_OPERATOR

RULES = SyntaxRules()


def _hasAttr(attr):
	def rule(parser, token):
		scope = parser.scope

		if not isinstance(token, type(Object)):
			if not ((VARIABLE == token) and (token.name in scope)):
				return None
			token = scope[token.name]

		return token.hasAttr(attr)

	return CustomTemplate.createToken(rule, f'_hasAttr({attr})')


def _runtimeRule(parser, inp):
	with inp.transaction():
		if not _hasAttr('__syntaxRule__')(parser, inp):
			return None

	syntaxRule = parser.scope[inp[0].name].getAttr('__syntaxRule__')
	return syntaxRule(parser, inp)


RULES.rawAdd(_runtimeRule)


@CustomTemplate.createToken
def _isAcceptableName(_, token):
	return isinstance(token, str) and (token.isalpha() or token in ('_',))


@CustomTemplate.createToken
def _isAcceptableContinuesName(_, token):
	return isinstance(token, str) and token.isdigit()


@RULES.add(
	_isAcceptableName,
	Maybe(Many(
		Or(
			[_isAcceptableName],
			[_isAcceptableContinuesName]
		)
	))
)
def _(*tokens):
	return [VARIABLE(''.join(tokens))]


@RULES.add(IsInstance(VARIABLE), Token(' '), Token('='), manualApply=True, useParser=True)
def _(inp, parser):
	inpRule = BufferRule(parser, inp)
	dst = inpRule.pop(IsInstance(VARIABLE)).one().name
	inpRule.pop(Token(' '), Token('='), Token(' '))

	parsed = parser.subParser(inp).parseLine()

	src = BufferRule(parser, Buffer.of(parsed.pop(-1))).pop(IsInstance(VARIABLE)).one().name

	return parsed + Buffer.of(SET_VARIABLE(dst, src))


@RULES.add(Or([Token('"')], [Token("'")]), manualApply=True, useParser=True)
def _(inp, parser):
	start = [inp.pop()]
	string = ''
	while not inp.startswith(start):
		string += inp.pop()
	while start:
		assert start.pop(0) == inp.pop()
	dst = VARIABLE.temp()
	parser.define(CALL_FUNCTION_STATIC(dst=dst.name, function=String.call, typeb='(', args=[string]))

	return Buffer.of(dst)


@CustomTemplate.createToken
def _isDigit(_, token):
	return isinstance(token, str) and token.isdigit()


@RULES.add(Many(_isDigit), Maybe(Token('.'), Many(_isDigit)), useParser=True)
def _(*args, parser=None):
	number = ''.join(args)
	dst = VARIABLE.temp()
	parser.define(CALL_FUNCTION_STATIC(dst=dst.name, function=Number.call, typeb='(', args=[number]))
	return [dst]


@RULES.add(
	IsInstance(VARIABLE),
	Token('('),
	Maybe(Many(IsInstance(VARIABLE), minMatches=1)),
	Token(')'),
	useParser=True
)
def _(function, opToken, *args, parser=None):
	args = [arg.name for arg in args[:-1]]
	dst = VARIABLE.temp()
	parser.define(CALL_FUNCTION(dst.name, function.name, opToken, args, {}))
	return [dst]


class UseCodeBlock:
	@classmethod
	def parse(cls, parser, inp):
		inpRule = BufferRule(parser, inp)
		var = inpRule.pop(_hasAttr('__useCodeBlock__')).one()
		inpRule.pop(Token(':'))
		code = cls.popCodeBlock(parser, inp)
		var = var.getAttr('__useCodeBlock__').call(code)
		return Buffer.of(var)

	@classmethod
	def isFullCodeBlock(cls, parser, inp):
		return BufferRule(parser, inp).startsWith(Token('\n'))

	@classmethod
	def popCodeBlock(cls, parser, inp):
		if cls.isFullCodeBlock(parser, inp):
			return cls.parseFullCodeBlock(parser, inp)
		return cls._parseInlineCodeBlock(parser, inp)

	@classmethod
	def parseFullCodeBlock(cls, parser, inp):
		inpRule = BufferRule(parser, inp)
		code = Buffer()
		inpRule.pop(Token('\n'))
		indent = cls._getFirstIndent(inpRule)

		while inpRule.startsWith(indent):
			inpRule.pop(indent)
			while inp and (not inpRule.startsWith(Token('\n'))):
				code.append(inp.pop())
			if inp:
				code.append(inp.pop())

		if code[-1] == '\n':
			inp.appFront(code.pop(-1))

		return parser.subParser(code)

	@staticmethod
	def _getFirstIndent(inpRule):
		indent = inpRule.get(Many(Token(' '))) or inpRule.get(Many(Token('\t')))

		assert len(set(indent)) == 1
		return Template(*map(Token, indent))

	@staticmethod
	def _parseInlineCodeBlock(parser, inp):
		while inp[0] == ' ':
			inp.pop()

		code = Buffer()

		while inp and (inp[0] != '\n'):
			code.append(inp.pop(0))

		return parser.subParser(code)


@RULES.add(_hasAttr('__useCodeBlock__'), Token(':'), manualApply=True, useParser=True)
def _(parser, inp):
	return UseCodeBlock.parse(parser, inp)


@RULES.add(IsInstance(VARIABLE), Token('.'), IsInstance(VARIABLE), useParser=True)
def _(first, token, attribute, parser):
	attributeVar = VARIABLE.temp()
	dst = VARIABLE.temp()

	parser.define(
		CALL_FUNCTION_STATIC(
			dst=attributeVar.name, function=String.call, typeb='(', args=[attribute.name]
		),
		CALL_OPERATOR(
			dst=dst.name, first=first.name, operator=token, second=attributeVar.name
		)
	)

	return [dst]
