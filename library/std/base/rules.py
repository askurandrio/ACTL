# pylint: disable=no-member
from actl.Buffer import TransactionBuffer, Buffer
from actl.objects import AToPy, AObject, PyToA
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
from actl.utils import generatorToAwaitable


RULES = SyntaxRules()


@RULES.rawAdd
class _ApplySyntaxObjectSyntaxRule:
	@classmethod
	async def match(cls, parser, inp):
		executeCoroutine = AToPy(parser.scope['__project__'])[
			'buildExecutor'
		].executeCoroutine

		async for syntaxObject in cls._getSyntaxObjects(parser, inp, executeCoroutine):
			syntaxRule = AToPy(
				executeCoroutine(syntaxObject.getAttribute('__syntaxRule__'))
			)
			if not isinstance(syntaxRule, list):
				syntaxRule = [syntaxRule]

			for rule in syntaxRule:
				if parser.rules.isDisabled(rule):
					continue

				apply = await rule.match(parser, inp)
				if apply:
					return apply

		return None

	@staticmethod
	async def _getSyntaxObjects(parser, inp, executeCoroutine):
		scope = parser.scope

		async for token in BufferRule(parser, TransactionBuffer(inp)).popUntil(
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
async def _isAcceptableName(_, token):
	return isinstance(token, str) and (token.isalpha() or token in ('_',))


@CustomTemplate.createToken
async def _isAcceptableContinuesName(_, token):
	return isinstance(token, str) and token.isdigit()


class VariableTemplate(Template):
	def __init__(self):
		super().__init__(
			_isAcceptableName,
			Maybe(Many(Or([_isAcceptableName], [_isAcceptableContinuesName]))),
		)

	async def __call__(self, parser, inp):
		tokens = await super().__call__(parser, TransactionBuffer(inp))

		if tokens is None:
			return None

		variable = VARIABLE(''.join(tokens))
		del inp[: len(list(tokens))]
		return [variable]


@RULES.add(Token('return '), Parsed(IsInstance(VARIABLE)))
async def _parseReturn(*args):
	*_, returnVar = args

	return [RETURN(returnVar.name)]


@RULES.add(VariableTemplate())
async def _parseVar(var):
	return [var]


@RULES.add(
	IsInstance(VARIABLE),
	Token(' '),
	Token('='),
	Token(' '),
	Parsed(IsInstance(VARIABLE)),
)
async def parseSetVariable(dst, _, _1, _2, src):
	return [SET_VARIABLE(dst.name, src.name)]


@RULES.add(Or([Token('"')], [Token("'")]), manualApply=True, useParser=True)
async def _parseString(inp, parser):
	start = [inp.pop()]
	string = ''
	while not inp.startsWith(start):
		string += inp.pop()
	while start:
		assert start.pop(0) == inp.pop()
	dst = parser.makeTmpVar()
	await generatorToAwaitable.of(
		CALL_FUNCTION_STATIC(dst=dst.name, function='String', staticArgs=[string])
	)

	inp.insert(0, [dst])


@RULES.add(IsInstance(VARIABLE), Token('('), manualApply=True, useParser=True)
class _ParseFunctionCall:
	def __init__(self, parser, inp):
		self._parser = parser
		self._inp = inp
		self._inpRule = BufferRule(self._parser, self._inp)

	async def _parseFunctionName(self):
		functionVar = (await self._inpRule.pop(IsInstance(VARIABLE))).one()
		return functionVar.name

	async def _parseArg(self):
		self._inpRule.parseUntil(Or([IsInstance(VARIABLE)], [Token(')')], [Token(',')]))

		if await self._inpRule.startsWith(IsInstance(VARIABLE)):
			var = (await self._inpRule.pop(IsInstance(VARIABLE))).one()
			self._inpRule.parseUntil(Or([Token('=')], [Token(')')], [Token(',')]))
			if await self._inpRule.startsWith(Token('=')):
				argName = var.name
				await self._inpRule.pop(Token('='))
			else:
				self._inp.insert(0, [var])
				argName = None
		else:
			argName = None

		argCode = await self._inpRule.pop(Parsed.until(Or([Token(')')], [Token(',')])))
		while argCode[-1] in (' ', '\n'):
			argCode.pop(-1)
		argVar = argCode.pop(-1).name
		await generatorToAwaitable.of(*argCode)
		return argName, argVar

	async def parse(self):
		functionName = await self._parseFunctionName()
		args = []
		kwargs = {}
		opToken = (await self._inpRule.pop(Token('('))).one()

		while True:
			await self._inpRule.pop(Many(Or([Token(' ')], [Token('\n')]), minMatches=0))
			if await self._inpRule.startsWith(Token(')')):
				break

			argName, argVar = await self._parseArg()
			if argName is None:
				assert not kwargs, kwargs
				args.append(argVar)
			else:
				kwargs[argName] = argVar

			await self._inpRule.pop(Many(Or([Token(' ')], [Token('\n')]), minMatches=0))
			await self._inpRule.pop(Token(','), default=None)

		await self._inpRule.pop(Token(')'))
		dst = self._parser.makeTmpVar()
		await generatorToAwaitable.of(
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

	async def parse(self):
		with self.parser.makeTmpVar.onNestedScope():
			if await self.isFullCodeBlock():
				return await self.parseFullCodeBlock()
			return self.parseInLineCodeBlock()

	async def isFullCodeBlock(self):
		return await self.inpRule.startsWith(Token('\n'))

	async def parseFullCodeBlock(self):
		code = Buffer()
		await self.inpRule.pop(Token('\n'))
		indent = await self.getFirstIndent()

		while await self.inpRule.startsWith(indent):
			await self.inpRule.pop(indent)
			while self.inp and (not await self.inpRule.startsWith(Token('\n'))):
				code.append(self.inp.pop())

			if await self.inpRule.startsWith(Token('\n')):
				code.append(self.inp.pop())

			while await self.inpRule.startsWith(
				Many(Or([Token(' ')], [Token('\t')]), minMatches=0), Token('\n')
			):
				async for _ in self.inpRule.popUntil(Token('\n')):
					pass
				await self.inpRule.pop(Token('\n'))

		if await self.inpRule.startsWith(
			Many(Or([Token(' ')], [Token('\t')])), Not(Or([Token(' ')], [Token('\t')]))
		):
			raise RuntimeError(
				f'Speces before code after block is forbidden: {self.inp}'
			)

		code.loadAll()
		if code[-1] == '\n':
			self.inp.insert(0, (code.pop(-1),))

		return tuple(self.parser.subParser(code))

	async def getFirstIndent(self):
		indent = await self.inpRule.get(Many(Token(' '))) or await self.inpRule.get(
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
async def _parseGetAttribute(object_, _, attribute, parser):
	dst = parser.makeTmpVar()

	await generatorToAwaitable.of(GET_ATTRIBUTE(dst.name, object_.name, attribute.name))

	return [dst]


@RULES.add(
	IsInstance(VARIABLE),
	Token('.'),
	IsInstance(VARIABLE),
	Token(' '),
	Token('='),
	Token(' '),
	Parsed(IsInstance(VARIABLE)),
)
async def _parseSetAttribute(object_, _, attribute, _1, _2, _3, src):
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
	Parsed(IsInstance(VARIABLE)),
	useParser=True,
)
async def _parseOperator(first, _, _1, second, operator, parser):
	dst = parser.makeTmpVar()
	operator = ''.join(operator)

	await generatorToAwaitable.of(
		CALL_OPERATOR(
			dst=dst.name, first=first.name, operator=operator, second=second.name
		)
	)

	return [dst]


async def _onLineStart(parser, _):
	if parser.onLineStart:
		return ()

	return None


@RULES.add(
	_onLineStart,
	Many(Or([Token(' ')], [Token('\t')])),
	Not(Or([Token(' ')], [Token('\t')], [Token('\n')])),
	manualApply=True,
)
async def _spacesBeforeCodeIsForbidden(inp):
	raise RuntimeError(f'Speces before code is forbidden: {inp}')


@RULES.add(
	_onLineStart, Or([Many(Token(' ')), Token('\n')], [Many(Token('\t')), Token('\n')])
)
async def _removeEmptyLine(*_):
	return ()


@RULES.add(Or([Token(' '), Token('\t')], [Token('\t'), Token(' ')]), manualApply=True)
async def _mixedIndentationIsForbidden(inp):
	raise RuntimeError(f'Mixed indentation is forbidden: {inp}')


def hasAttribute(attribute):
	async def match(parser, inp):
		executeCoroutine = AToPy(parser.scope['__project__'])[
			'buildExecutor'
		].executeCoroutine
		token = inp[0]

		if not isinstance(token, AObject):
			if (VARIABLE != inp[0]) or (inp[0].name not in parser.scope):
				return

			token = parser.scope[inp[0].name]

		if not executeCoroutine(token.hasAttribute(attribute)):
			return

		inp.pop(0)
		return [token]

	return match


@RULES.add(Or([Token(' '), Token('\t')], [Token('\t'), Token(' ')]), manualApply=True)
async def _mixedIndentationIsForbidden(inp):
	raise RuntimeError(f'Mixed indentation is forbidden: {inp}')


@RULES.add(
	hasAttribute('__useCodeBlock__'), Token(':'), useParser=True, manualApply=True
)
async def _parseUseCodeBlock(parser, inp):
	var = inp.pop(0)
	inp.pop(0)

	executeCoroutine = AToPy(parser.scope['__project__'])[
		'buildExecutor'
	].executeCoroutine

	async def callUseCodeBlock():
		useCodeBlockMethod = await var.getAttribute('__useCodeBlock__')

		codeBlock = CodeBlock(parser, inp)
		aCodeBlock = await PyToA.call(codeBlock)
		result = await useCodeBlockMethod.call(aCodeBlock)

		return AToPy(result)

	parseFunc, applyFunc = executeCoroutine(callUseCodeBlock())

	await parseFunc()
	executeCoroutine(applyFunc())
