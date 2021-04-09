# pylint: disable=no-member
from actl.Buffer import LTransactionBuffer, Buffer
from actl.objects import String, Number, Object, Vector
from actl.syntax import SyntaxRules, CustomTemplate, IsInstance, Many, Or, Token, Maybe, Template, \
	BufferRule, Parsed, Frame
from actl.opcodes import VARIABLE, SET_VARIABLE, CALL_FUNCTION, CALL_FUNCTION_STATIC, CALL_OPERATOR

RULES = SyntaxRules()


def _hasAttr(attr):
	def rule(parser, token):
		scope = parser.scope

		if not isinstance(token, type(Object)):
			if not ((VARIABLE == token) and (token.name in scope)):
				return None
			token = scope[token.name]

		return token.hasAttribute(attr)

	return CustomTemplate.createToken(rule, f'_hasAttr({attr})')


def _applySyntaxObjectsRule(parser, inp):
	hasAttrSyntaxRule = _hasAttr('__syntaxRule__')
	if not hasAttrSyntaxRule(parser, LTransactionBuffer(inp)):
		return None

	syntaxRule = parser.scope[inp[0].name].getAttribute('__syntaxRule__')
	return syntaxRule(parser, inp)


RULES.rawAdd(_applySyntaxObjectsRule)


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
	parser.subParser(inp).parseLine()
	parsed = BufferRule(parser, inp).popUntil(parser.endLine).loadAll()

	src = BufferRule(parser, Buffer.of(parsed.pop(-1))).pop(IsInstance(VARIABLE)).one().name

	inp.insert(0, parsed + Buffer.of(SET_VARIABLE(dst, src)))


@RULES.add(Or([Token('"')], [Token("'")]), manualApply=True, useParser=True)
def _(inp, parser):
	start = [inp.pop()]
	string = ''
	while not inp.startsWith(start):
		string += inp.pop()
	while start:
		assert start.pop(0) == inp.pop()
	dst = parser.makeTmpVar()
	parser.define(CALL_FUNCTION_STATIC(dst=dst.name, function=String.call, args=[string]))

	inp.insert(0, [dst])


@CustomTemplate.createToken
def _isDigit(_, token):
	return isinstance(token, str) and token.isdigit()


@RULES.add(Maybe(Token('-')), Many(_isDigit), Maybe(Token('.'), Many(_isDigit)), useParser=True)
def _(*args, parser=None):
	number = ''.join(args)
	dst = parser.makeTmpVar()
	parser.define(CALL_FUNCTION_STATIC(dst=dst.name, function=Number.call, args=[number]))
	return [dst]


@RULES.add(
	IsInstance(VARIABLE),
	Token('('),
	manualApply=True,
	useParser=True
)
class _ParseFunctionCall:
	def __init__(self, parser, inp):
		self._parser = parser
		self._inp = inp
		self._inpRule = BufferRule(self._parser, self._inp)

	def _parseFunctionName(self):
		functionVar = self._inpRule.pop(IsInstance(VARIABLE)).one()
		return functionVar.name

	def _parseArg(self):
		self._inpRule.parseUntil(Or([IsInstance(VARIABLE)], [Token(')')], [Token(',')]))

		if self._inpRule.startsWith(IsInstance(VARIABLE)):
			var = self._inpRule.pop(IsInstance(VARIABLE)).one()
			self._inpRule.parseUntil(Or([Token('=')], [Token(')')], [Token(',')]))
			if self._inpRule.startsWith(Token('=')):
				argName = var.name
				self._inpRule.pop(Token('='))
			else:
				self._inp.insert(0, [var])
				argName = None
		else:
			argName = None

		argCode = self._inpRule.pop(Frame(Or([Token(')')], [Token(',')])))
		argVar = argCode.pop(-1).name
		self._parser.define(*argCode)
		return argName, argVar

	def parse(self):
		functionName = self._parseFunctionName()
		args = []
		kwargs = {}
		opToken = self._inpRule.pop(Token('(')).one()

		while not self._inpRule.startsWith(Token(')')):
			argName, argVar = self._parseArg()
			if argName is None:
				assert not kwargs, kwargs
				args.append(argVar)
			else:
				kwargs[argName] = argVar

			self._inpRule.pop(Token(','), Token(' '), default=None)

		self._inpRule.pop(Token(')'))
		dst = self._parser.makeTmpVar()
		self._parser.define(CALL_FUNCTION(dst.name, functionName, opToken, args, kwargs))
		self._inp.insert(0, [dst])


@RULES.add(_hasAttr('__onCodeBlock__'), Token(':'), manualApply=True, useParser=True)
class OnCodeBlock:
	def __init__(self, parser, inp):
		self.parser = parser
		self.inp = inp
		self.inpRule = BufferRule(parser, inp)
		self._var = None

	def parse(self):
		self._parseCodeBlockOpen()
		self._var.getAttribute('__useCodeBlock__').call(self)

	def _parseCodeBlockOpen(self):
		self._var = self.inpRule.pop(IsInstance(type(Object))).one()
		self.inpRule.pop(Token(':'))


@RULES.add(_hasAttr('__useCodeBlock__'), Token(':'), manualApply=True, useParser=True)
class UseCodeBlock(OnCodeBlock):
	def parse(self):
		self._parseCodeBlockOpen()
		code = self.popCodeBlock()
		code = self._var.getAttribute('__useCodeBlock__').call(code)
		self.inp.insert(0, code)

	def isFullCodeBlock(self):
		return self.inpRule.startsWith(Token('\n'))

	def popCodeBlock(self):
		with self.parser.makeTmpVar.onNestedScope():
			if self.isFullCodeBlock():
				return self.parseFullCodeBlock()
			return self.parseInLineCodeBlock()

	def parseFullCodeBlock(self):
		code = Buffer()
		self.inpRule.pop(Token('\n'))
		indent = self.getFirstIndent()

		while self.inpRule.startsWith(indent):
			self.inpRule.pop(indent)
			while self.inp and (not self.inpRule.startsWith(Token('\n'))):
				code.append(self.inp.pop())
			if self.inp:
				code.append(self.inp.pop())

		code.loadAll()
		if code[-1] == '\n':
			self.inp.insert(0, (code.pop(-1),))

		return tuple(self.parser.subParser(code))

	def getFirstIndent(self):
		indent = self.inpRule.get(Many(Token(' '))) or self.inpRule.get(Many(Token('\t')))

		assert len(set(indent)) == 1
		return Template(*map(Token, indent))

	def parseInLineCodeBlock(self):
		while self.inp[0] == ' ':
			self.inp.pop()

		code = Buffer()

		while self.inp and (self.inp[0] != '\n'):
			code.append(self.inp.pop())

		return tuple(self.parser.subParser(code))


@RULES.add(IsInstance(VARIABLE), Token('.'), IsInstance(VARIABLE), useParser=True)
def _(first, token, attribute, parser):
	attributeVar = parser.makeTmpVar()
	dst = parser.makeTmpVar()

	parser.define(
		CALL_FUNCTION_STATIC(
			dst=attributeVar.name, function=String.call, args=[attribute.name]
		),
		CALL_OPERATOR(
			dst=dst.name, first=first.name, operator=token, second=attributeVar.name
		)
	)

	return [dst]


@RULES.add(
	IsInstance(VARIABLE), Token(' '), Token('+'), Token(' '), Parsed(IsInstance(VARIABLE)),
	useParser=True
)
def _(first, _, token, _1, second, parser):
	dst = parser.makeTmpVar()

	parser.define(
		CALL_OPERATOR(dst=dst.name, first=first.name, operator=token, second=second.name)
	)

	return [dst]


@RULES.add(Token('['), manualApply=True, useParser=True)
def _(parser, inp):
	inpRule = BufferRule(parser, inp)
	inpRule.pop(Token('['))
	dst = parser.makeTmpVar()
	parser.define(CALL_FUNCTION_STATIC(dst=dst.name, function=Vector.call, args=[]))

	if not inpRule.startsWith(Token(']')):
		appendStrVar = parser.makeTmpVar()
		appendVarName = parser.makeTmpVar().name
		parser.define(
			CALL_FUNCTION_STATIC(dst=appendStrVar.name, function=String.call, args=['append']),
			CALL_OPERATOR(dst=appendVarName, first=dst.name, operator='.', second=appendStrVar.name)
		)

		while not inpRule.startsWith(Token(']')):
			elementCode = inpRule.pop(Frame(Or([Token(']')], [Token(',')])))
			elementVarName = elementCode.pop(-1).name
			parser.define(
				*elementCode,
				CALL_FUNCTION('__IV0', appendVarName, args=[elementVarName])
			)

	inpRule.pop(Token(']'))
	inp.insert(0, [dst])
