from actl.syntax import *
from actl.opcodes import *
from actl.objects import NativeFunction, PyToA
from actl import executeSyncCoroutine, generatorToAwaitable
from std.base.executor import bindExecutor
from std.base.rules import RULES as stdRULES, parseSetVariable


RULES = SyntaxRules(stdRULES)


@RULES.add(IsInstance(VARIABLE), Token('['), manualApply=True, useParser=True)
async def _parseSlice(parser, inp):
	inpRule = BufferRule(parser, inp)
	collectionVariable = (await inpRule.pop(IsInstance(VARIABLE))).one()
	await inpRule.pop(Token('['))

	startVariable = (await inpRule.pop(Parsed.until(Token(':')))).one()

	await inpRule.pop(Token(':]'))

	sliceVariable = parser.makeTmpVar()
	await generatorToAwaitable.of(
		CALL_FUNCTION_STATIC(
			dst=sliceVariable.name,
			function='Slice',
			args=[startVariable.name, 'None', 'None'],
		)
	)

	getItemMethodVariable = parser.makeTmpVar()
	await generatorToAwaitable.of(
		GET_ATTRIBUTE(
			getItemMethodVariable.name, collectionVariable.name, '__getItem__'
		)
	)

	subCollectionVariable = parser.makeTmpVar()
	await generatorToAwaitable.of(
		CALL_FUNCTION(
			subCollectionVariable.name,
			getItemMethodVariable.name,
			args=[sliceVariable.name],
		)
	)

	inp.insert(0, [subCollectionVariable])


@RULES.add(Token('['), manualApply=True, useParser=True)
async def _parseVector(parser, inp):
	inpRule = BufferRule(parser, inp)
	await inpRule.pop(Token('['))
	dst = parser.makeTmpVar()
	await generatorToAwaitable.of(CALL_FUNCTION_STATIC(dst=dst.name, function='Vector'))

	if not await inpRule.startsWith(Token(']')):
		appendVarName = parser.makeTmpVar().name
		await generatorToAwaitable.of(GET_ATTRIBUTE(appendVarName, dst.name, 'append'))
		appendResultVarName = parser.makeTmpVar().name

		while not await inpRule.startsWith(Token(']')):
			elementCode = await inpRule.pop(
				Parsed.until(Or([Token(']')], [Token(',')]))
			)
			elementVarName = elementCode.pop(-1).name
			await generatorToAwaitable.of(
				*elementCode,
				CALL_FUNCTION(appendResultVarName, appendVarName, args=[elementVarName])
			)

	await inpRule.pop(Token(']'))
	inp.insert(0, [dst])


@NativeFunction
async def vector__of(*args):
	executor = await bindExecutor()
	Vector = executor.scope['Vector']
	vector = await Vector.call()
	append = await vector.getAttribute('append')
	for element in args:
		await append.call(element)

	return vector


@RULES.add(
	IsInstance(VARIABLE),
	Token(', '),
	Disable(
		[parseSetVariable, '_parseConstVector', '_parseSetWithUnpack'],
		[
			IsInstance(VARIABLE),
			Parsed(
				Many(Token(','), Maybe(Token(' ')), IsInstance(VARIABLE), minMatches=0)
			),
		],
	),
	Not(Token(' '), Token('=')),
	useParser=True,
)
async def _parseConstVector(*inp, parser):
	args = [arg.name for arg in inp if VARIABLE == arg]
	dst = parser.makeTmpVar()

	await generatorToAwaitable.of(
		CALL_FUNCTION_STATIC(dst.name, vector__of.call, args=args)
	)

	return [dst]


@RULES.add(
	IsInstance(VARIABLE),
	Token(', '),
	Disable(
		[parseSetVariable, '_parseConstVector', '_parseSetWithUnpack'],
		[
			IsInstance(VARIABLE),
			Parsed(
				Many(Token(','), Maybe(Token(' ')), IsInstance(VARIABLE), minMatches=0)
			),
		],
	),
	Token(' '),
	Token('='),
	Token(' '),
	Parsed(IsInstance(VARIABLE)),
	useParser=True,
)
async def _parseSetWithUnpack(*inp, parser):
	with parser.makeTmpVar.onNestedScope():
		srcAsIter = parser.makeTmpVar().name
		srcIterNext = parser.makeTmpVar().name

	await generatorToAwaitable.of(
		CALL_FUNCTION(srcAsIter, 'Iter', args=[inp[-1].name]),
		GET_ATTRIBUTE(srcIterNext, srcAsIter, 'next'),
	)

	for arg in inp:
		if VARIABLE == arg:
			await generatorToAwaitable.of(CALL_FUNCTION(arg.name, srcIterNext))
			continue

		if '=' == arg:
			break

	return ()


@CustomTemplate.createToken
async def _isDigit(_, token):
	return isinstance(token, str) and token.isdigit()


@RULES.add(
	Maybe(Token('-')), Many(_isDigit), Maybe(Token('.'), Many(_isDigit)), useParser=True
)
async def _parseNumber(*args, parser=None):
	number = ''.join(args)
	aProxy = executeSyncCoroutine(PyToA.call(number))
	dst = parser.makeTmpVar()
	await generatorToAwaitable.of(
		CALL_FUNCTION_STATIC(dst=dst.name, function='Number', staticArgs=[aProxy])
	)
	return [dst]
