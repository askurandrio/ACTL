# pylint: disable=no-member
from actl.Buffer import TransactionBuffer, Buffer
from actl.objects import AToPy, AObject
from actl.opcodes.opcodes import RETURN
from actl.syntax import *
from actl.opcodes import (
	VARIABLE,
	SET_VARIABLE,
	CALL_FUNCTION,
	CALL_FUNCTION_STATIC,
	CALL_OPERATOR,
	GET_ATTRIBUTE,
	SET_ATTRIBUTE,
)


RULES = SyntaxRules()


@RULES.rawAdd
class _ApplySyntaxObjectSyntaxRule:
	@classmethod
	def match(cls, parser, inp):
		executeCoroutine = AToPy(parser.scope['__project__'])[
			'buildExecutor'
		].executeCoroutine

		for syntaxObject in cls._getSyntaxObjects(parser, inp, executeCoroutine):
			syntaxRule = executeCoroutine(syntaxObject.getAttribute('__syntaxRule__'))
			if not isinstance(syntaxRule, list):
				syntaxRule = [syntaxRule]

			for rule in syntaxRule:
				apply = rule.match(parser, inp)
				if apply:
					return apply

		return None

	@staticmethod
	def _getSyntaxObjects(parser, inp, executeCoroutine):
		scope = parser.scope

		for token in BufferRule(parser, TransactionBuffer(inp)).popUntil(
			parser.endLine
		):
			if (VARIABLE != token) or (token.name not in scope):
				continue

			tokenValue = scope[token.name]
			if isinstance(tokenValue, AObject) and executeCoroutine(
				tokenValue.hasAttribute('__syntaxRule__')
			):
				yield tokenValue


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
			Maybe(Many(Or([_isAcceptableName], [_isAcceptableContinuesName]))),
		)

	def __call__(self, parser, inp):
		tokens = super().__call__(parser, TransactionBuffer(inp))

		if tokens is None:
			return None

		variable = VARIABLE(''.join(tokens))
		del inp[: len(list(tokens))]
		return [variable]


@RULES.add(Token('return '), Parsed(), IsInstance(VARIABLE))
def _parseReturn(*args):
	*_, returnVar = args

	return [RETURN(returnVar.name)]


@RULES.add(VariableTemplate())
def _parseVar(var):
	return [var]


@RULES.add(
	IsInstance(VARIABLE),
	Token(' '),
	Token('='),
	Token(' '),
	Parsed(),
	IsInstance(VARIABLE),
)
def parseSetVariable(dst, _, _1, _2, src):
	return [SET_VARIABLE(dst.name, src.name)]


@RULES.add(Or([Token('"')], [Token("'")]), manualApply=True, useParser=True)
def _parseString(inp, parser):
	start = [inp.pop()]
	string = ''
	while not inp.startsWith(start):
		string += inp.pop()
	while start:
		assert start.pop(0) == inp.pop()
	dst = parser.makeTmpVar()
	parser.define(
		CALL_FUNCTION_STATIC(dst=dst.name, function='String', staticArgs=[string])
	)

	inp.insert(0, [dst])


@RULES.add(IsInstance(VARIABLE), Token('('), manualApply=True, useParser=True)
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

		while True:
			self._inpRule.pop(Many(Or([Token(' ')], [Token('\n')]), minMatches=0))
			if self._inpRule.startsWith(Token(')')):
				break

			argName, argVar = self._parseArg()
			if argName is None:
				assert not kwargs, kwargs
				args.append(argVar)
			else:
				kwargs[argName] = argVar

			self._inpRule.pop(Token(','), Token(' '), default=None)

		self._inpRule.pop(Token(')'))
		dst = self._parser.makeTmpVar()
		self._parser.define(
			CALL_FUNCTION(
				dst.name, functionName, typeb=opToken, args=args, kwargs=kwargs
			)
		)
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
				tuple(self.inpRule.popUntil(Token('\n')))
				self.inpRule.pop(Token('\n'))

		if self.inpRule.startsWith(
			Many(Or([Token(' ')], [Token('\t')])), Not(Or([Token(' ')], [Token('\t')]))
		):
			raise RuntimeError(
				f'Speces before code after block is forbidden: {self.inp}'
			)

		code.loadAll()
		if code[-1] == '\n':
			self.inp.insert(0, (code.pop(-1),))

		return tuple(self.parser.subParser(code))

	def getFirstIndent(self):
		indent = self.inpRule.get(Many(Token(' '))) or self.inpRule.get(
			Many(Token('\t'))
		)

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
	useParser=True,
)
def _parseGetAttribute(object_, _, attribute, parser):
	dst = parser.makeTmpVar()

	parser.define(GET_ATTRIBUTE(dst.name, object_.name, attribute.name))

	return [dst]


@RULES.add(
	IsInstance(VARIABLE),
	Token('.'),
	IsInstance(VARIABLE),
	Token(' '),
	Token('='),
	Token(' '),
	Parsed(),
	IsInstance(VARIABLE),
)
def _parseSetAttribute(object_, _, attribute, _1, _2, _3, src):
	return [SET_ATTRIBUTE(object=object_.name, attribute=attribute.name, src=src.name)]


@RULES.add(
	IsInstance(VARIABLE),
	Token(' '),
	CustomTemplate.asArg(
		Or(
			(Token('+'),),
			(Token('-'),),
			(Token('*'),),
			(Token('/'),),
			(Token('<='),),
			(Token('>='),),
			(Token('<'),),
			(Token('>'),),
			(Token('!='),),
			(Token('=='),),
		),
		'operator',
	),
	Token(' '),
	Parsed(),
	IsInstance(VARIABLE),
	useParser=True,
)
def _parseOperator(first, _, _1, second, operator, parser):
	dst = parser.makeTmpVar()
	operator = ''.join(operator)

	parser.define(
		CALL_OPERATOR(
			dst=dst.name, first=first.name, operator=operator, second=second.name
		)
	)

	return [dst]


def _onLineStart(parser, _):
	if parser.onLineStart:
		return ()

	return None


@RULES.add(
	_onLineStart,
	Many(Or([Token(' ')], [Token('\t')])),
	Not(Or([Token(' ')], [Token('\t')], [Token('\n')])),
	manualApply=True,
)
def _spacesBeforeCodeIsForbidden(inp):
	raise RuntimeError(f'Speces before code is forbidden: {inp}')


@RULES.add(
	_onLineStart, Or([Many(Token(' ')), Token('\n')], [Many(Token('\t')), Token('\n')])
)
def _removeEmptyLine(*_):
	return ()


@RULES.add(Or([Token(' '), Token('\t')], [Token('\t'), Token(' ')]), manualApply=True)
def _mixedIndentationIsForbidden(inp):
	raise RuntimeError(f'Mixed indentation is forbidden: {inp}')
