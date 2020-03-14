# pylint: disable=no-member

from actl.objects import String, Number, AbstractObject
from actl.syntax import SyntaxRules, CustomTemplate, IsInstance, Many, Or, Token, Maybe, Buffer, \
	Template, BufferRule
from actl.opcodes import \
	VARIABLE, SET_VARIABLE, CALL_FUNCTION, CALL_FUNCTION_STATIC


RULES = SyntaxRules()


def _hasAttr(attr):
	def rule(parser, token):
		scope = parser.scope

		if not isinstance(token, AbstractObject):
			if not ((VARIABLE == token) and (token.name in scope)):
				return None
			token = scope[token.name]

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


@RULES.add(IsInstance(VARIABLE), Token(' '), Token('='), manualApply=True, useParser=True)
def _(inp, parser):
	dst = inp.pop()
	assert inp.pop() == ' '
	assert inp.pop() == '='
	assert inp.pop() == ' '

	parsed = parser.subParser(inp).parseLine()
	src = parsed.pop(-1)
	assert isinstance(src, VARIABLE)

	inp.set_(parsed + Buffer.of(SET_VARIABLE(dst.name, src.name)) + inp)


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
	inp.set_(Buffer.of(dst) + inp)


@CustomTemplate.createToken
def _is_digit(_, token):
	return isinstance(token, str) and token.isdigit()


@RULES.add(Many(_is_digit), Maybe(Token('.'), Many(_is_digit)), useParser=True)
def _(*args, parser=None):
	number = ''.join(args)
	dst = VARIABLE.temp()
	parser.define(CALL_FUNCTION_STATIC(dst=dst.name, function=Number.call, typeb='(', args=[number]))
	return [dst]


@RULES.add(
	IsInstance(VARIABLE),
	Token('('),
	Maybe(Many(IsInstance(VARIABLE), min_matches=1)),
	Token(')'),
	useParser=True
)
def _(function, op_token, *args, parser=None):
	args = [arg.name for arg in args[:-1]]
	dst = VARIABLE.temp()
	parser.define(CALL_FUNCTION(dst.name, function.name, op_token, args, {}))
	return [dst]


@RULES.add(_hasAttr('__useCodeBlock__'), Token(':'), manualApply=True, useParser=True)
class UseCodeBlock:
	def __init__(self, parser, inp):
		var = inp.pop()
		assert inp.pop() == ':'
		code = self.popCodeBlock(parser, inp)

		var = var.getAttr('__useCodeBlock__').call(code)
		inp.set_(Buffer.of(var) + inp)

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
		code = Buffer()
		inp.pop()
		indent = cls._getFirstIndent(parser, inp)

		while BufferRule(parser, inp).startsWith(indent):
			BufferRule(parser, inp).pop(indent)
			while inp and (not BufferRule(parser, inp).startsWith(Token('\n'))):
				code.append(inp.pop())
			if inp:
				code.append(inp.pop())

		return parser.subParser(code)

	@staticmethod
	def _getFirstIndent(parser, inp):
		indent = BufferRule(parser, inp).get(Many(Token(' '))) or \
			BufferRule(parser, inp).get(Many(Token('\t')))

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
