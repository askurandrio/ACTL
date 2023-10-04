from actl.opcodes.opcodes import SET_VARIABLE
from actl.syntax import (
	SyntaxRule,
	Value,
	Token,
	IsInstance,
	Disable,
	Parsed,
	Many,
	Or,
	End,
	BufferRule,
	Maybe,
)
from actl.opcodes import CALL_FUNCTION_STATIC, VARIABLE, GET_ATTRIBUTE
from actl.objects import NativeFunction, Object, AToPy, ANone, PyToA
from actl import asDecorator, Buffer
from actl.utils import executeSyncCoroutine
from std.base.executor.utils import bindExecutor


From = executeSyncCoroutine(Object.call())


@NativeFunction
async def import_(importName):
	executor = await bindExecutor()
	project = AToPy(executor.scope['__project__'])
	module = await project['import'].importByName(importName)
	return module


@NativeFunction
async def copyAlllIntoScope(module, scope):
	scope = AToPy(scope)
	for key, value in AToPy(await module.getAttribute('__scope__')).getDiff():
		scope[key] = value

	return ANone


@asDecorator(
	lambda rule: executeSyncCoroutine(
		import_.setAttribute('__syntaxRule__', executeSyncCoroutine(PyToA.call(rule)))
	)
)
@SyntaxRule.wrap(
	Value(import_),
	Token(' '),
	IsInstance(VARIABLE),
	Disable(
		['_parseGetAttribute'],
		[Parsed(Many(Token('.'), IsInstance(VARIABLE), minMatches=0))],
	),
	Maybe(
		Token(' '),
		Token.of(VARIABLE('as')),
		Token(' '),
		IsInstance(VARIABLE),
	),
	useParser=True,
)
async def _parseImport(*args, parser=None):
	args = BufferRule(parser, Buffer(args))
	await args.pop(Value(import_), Token(' '))

	mainModuleName = (await args.pop(IsInstance(VARIABLE))).one().name
	moduleNames = tuple(await Buffer.loadAsync(args.popUntil(Or([Token(' ')], [End]))))

	if await args.startsWith(Token(' '), Token.of(VARIABLE('as'))):
		await args.pop(Token(' '), Token.of(VARIABLE('as')), Token(' '))
		resultName = (await args.pop(IsInstance(VARIABLE))).one().name
	else:
		resultName = mainModuleName

	res = [CALL_FUNCTION_STATIC(resultName, import_.call, staticArgs=(mainModuleName,))]

	if moduleNames:
		if not resultName.startswith('_tmpVar'):
			tmpResultName = parser.makeTmpVar().name
			res.append(SET_VARIABLE(tmpResultName, resultName))
			resultName = tmpResultName

		for moduleName in moduleNames:
			if moduleName == '.':
				continue

			res.append(GET_ATTRIBUTE(resultName, resultName, moduleName.name))

	return res


@asDecorator(
	lambda rule: executeSyncCoroutine(
		From.setAttribute('__syntaxRule__', executeSyncCoroutine(PyToA.call(rule)))
	)
)
@SyntaxRule.wrap(
	Value(From),
	Token(' '),
	IsInstance(VARIABLE),
	Disable(
		['_parseGetAttribute', '_parseImport'],
		[Parsed(Many(Token('.'), IsInstance(VARIABLE), minMatches=0))],
	),
	Token(' '),
	Value(import_),
	Token(' '),
	Or([IsInstance(VARIABLE)], [Token('*')]),
	useParser=True,
)
async def _parseFromImport(*args, parser=None):
	args = BufferRule(parser, Buffer(args))
	await args.pop(Value(From), Token(' '))

	codeModuleName = tuple(await Buffer.loadAsync(args.popUntil(Token(' '))))
	await args.pop(Token(' '))
	codeModuleImport = Buffer(
		(
			*(await args.pop(Value(import_))),
			' ',
			*codeModuleName,
			*' as ',
			parser.makeTmpVar(),
		)
	)
	res = [*parser.subParser(Buffer(codeModuleImport))]
	await args.pop(Token(' '))
	moduleVarName = res[-1].dst

	for attributeName in args:
		if '*' == attributeName:
			res.append(
				CALL_FUNCTION_STATIC(
					'_', copyAlllIntoScope.call, args=(moduleVarName, '__scope__')
				)
			)
			continue

		res.append(GET_ATTRIBUTE(attributeName.name, moduleVarName, attributeName.name))

	return res
