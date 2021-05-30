# pylint: disable=no-member
from actl.Buffer import TransactionBuffer, Buffer
from actl.objects import String, Number
from actl.opcodes.opcodes import RETURN
from actl.syntax import SyntaxRules, CustomTemplate, IsInstance, Many, Or, Token, Maybe, Template, \
	BufferRule, Parsed, Not, BreakPoint, AbstractTemplate
from actl.opcodes import VARIABLE, SET_VARIABLE, CALL_FUNCTION, CALL_FUNCTION_STATIC, \
	CALL_OPERATOR, GET_ATTRIBUTE, SET_ATTRIBUTE


RULES = SyntaxRules()


@RULES.rawAdd
class _ApplySyntaxObjectSyntaxRule:
	@classmethod
	def match(cls, parser, inp):
		for syntaxObject in cls._getSyntaxObjects(parser, inp):
			syntaxRule = syntaxObject.getAttribute('__syntaxRule__')
			if not isinstance(syntaxRule, list):
				syntaxRule = [syntaxRule]

			for rule in syntaxRule:
				apply = rule.match(parser, inp)
				if apply:
					return apply

	@staticmethod
	def _getSyntaxObjects(parser, inp):
		scope = parser.scope

		for token in BufferRule(parser, TransactionBuffer(inp)).popUntil(parser.endLine):
			if (VARIABLE != token) or (token.name not in scope):
				continue

			token = scope[token.name]
			if token.hasAttribute('__syntaxRule__'):
				yield token


@CustomTemplate.createToken
def _isAcceptableName(_, token):
	return isinstance(token, str) and (token.isalpha() or token in ('_',))


@CustomTemplate.createToken
def _isAcceptableContinuesName(_, token):
	return isinstance(token, str) and token.isdigit()


class VariableTemplate(Template):
	def __init__(self):
		super().__init__(
			_isAcceptableName,
			Maybe(Many(
				Or(
					[_isAcceptableName],
					[_isAcceptableContinuesName]
				)
			))
		)

	def __call__(self, parser, inp):
		tokens = super().__call__(parser, TransactionBuffer(inp))

		if tokens is None:
			return None

		variable = VARIABLE(''.join(tokens))
		del inp[:len(list(tokens))]
		return [variable]


@RULES.add(Token('return '), Parsed(), IsInstance(VARIABLE))
def _parseReturn(*args):
	*_, returnVar = args

	return [
		RETURN(returnVar.name)
	]


@RULES.add(VariableTemplate())
def _parseVar(var):
	return [var]


@RULES.add(
	IsInstance(VARIABLE),
	Token(' '),
	Token('='),
	Token(' '),
	Parsed(),
	IsInstance(VARIABLE)
)
def _parseSetVariable(dst, _, _1, _2, src):
	return [
		SET_VARIABLE(dst.name, src.name)
	]


@RULES.add(Or([Token('"')], [Token("'")]), manualApply=True, useParser=True)
def _parseString(inp, parser):
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
def _parseNumber(*args, parser=None):
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

		argCode = self._inpRule.pop(Parsed(Or([Token(')')], [Token(',')])))
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


class CodeBlock:
	def __init__(self, parser, inp):
		self.parser = parser
		self.inp = inp
		self.inpRule = BufferRule(parser, inp)
		self._var = None

	def parse(self):
		with self.parser.makeTmpVar.onNestedScope():
			if self.isFullCodeBlock():
				return self.parseFullCodeBlock()
			return self.parseInLineCodeBlock()

	def isFullCodeBlock(self):
		return self.inpRule.startsWith(Token('\n'))

	def parseFullCodeBlock(self):
		code = Buffer()
		self.inpRule.pop(Token('\n'))
		indent = self.getFirstIndent()

		while self.inpRule.startsWith(indent):
			self.inpRule.pop(indent)
			while self.inp and (not self.inpRule.startsWith(Token('\n'))):
				code.append(self.inp.pop())

			if self.inpRule.startsWith(Token('\n')):
				code.append(self.inp.pop())

			while self.inpRule.startsWith(
				Many(Or([Token(' ')], [Token('\t')]), minMatches=0), Token('\n')
			):
				self.inpRule.popUntil(Token('\n'))
				self.inpRule.pop(Token('\n'))

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


@RULES.add(
	IsInstance(VARIABLE),
	Token('.'),
	VariableTemplate(),
	Not(Token(' '), Token('=')),
	useParser=True
)
def _parseGetAttribute(object_, _, attribute, parser):
	dst = parser.makeTmpVar()

	parser.define(
		GET_ATTRIBUTE(
			dst=dst.name, object=object_.name, attribute=attribute.name
		)
	)

	return [dst]


@RULES.add(
	IsInstance(VARIABLE),
	Token('.'),
	IsInstance(VARIABLE),
	Token(' '),
	Token('='),
	Token(' '),
	Parsed(),
	IsInstance(VARIABLE)
)
def _parseSetAttribute(object_, _, attribute, _1, _2, _3, src):
	return [
		SET_ATTRIBUTE(
			object=object_.name, attribute=attribute.name, src=src.name
		)
	]


@RULES.add(
	IsInstance(VARIABLE),
	Token(' '),
	Token('+'),
	Token(' '),
	Parsed(),
	IsInstance(VARIABLE),
	useParser=True
)
def _parseAdd(first, _, token, _1, second, parser):
	dst = parser.makeTmpVar()

	parser.define(
		CALL_OPERATOR(dst=dst.name, first=first.name, operator=token, second=second.name)
	)

	return [dst]
