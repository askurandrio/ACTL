from actl.opcodes.opcodes import SET_VARIABLE
from actl.syntax import (
	SyntaxRule,
	Value,
	Token,
	IsInstance,
	MatchParsed,
	Many,
	Or,
	End,
	BufferRule,
	Maybe,
)
from actl.opcodes import CALL_FUNCTION_STATIC, VARIABLE, GET_ATTRIBUTE
from actl.objects import NativeFunction, Object, AToPy, ANone
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
	for key, value in (await module.getAttribute('__scope__')).getDiff():
		scope[key] = value

	return ANone


@asDecorator(
	lambda rule: executeSyncCoroutine(import_.setAttribute('__syntaxRule__', rule))
)
@SyntaxRule.wrap(
	Value(import_),
	Token(' '),
	IsInstance(VARIABLE),
	Many(Token('.'), MatchParsed(IsInstance(VARIABLE)), minMatches=0),
	Maybe(
		Token(' '),
		MatchParsed(Token.of(VARIABLE('as')), Token(' '), IsInstance(VARIABLE)),
	),
	useParser=True,
)
def _parseImport(*args, parser=None):
	args = BufferRule(parser, Buffer(args))
	args.pop(Value(import_), Token(' '))

	mainModuleName = args.pop(IsInstance(VARIABLE)).one().name
	moduleNames = tuple(args.popUntil(Or([Token(' ')], [End])))

	if args.startsWith(Token(' '), Token.of(VARIABLE('as'))):
		args.pop(Token(' '), Token.of(VARIABLE('as')), Token(' '))
		resultName = args.pop(IsInstance(VARIABLE)).one().name
	else:
		resultName = mainModuleName

	yield CALL_FUNCTION_STATIC(resultName, import_.call, staticArgs=(mainModuleName,))

	if moduleNames:
		if not resultName.startswith('_tmpVar'):
			tmpResultName = parser.makeTmpVar().name
			yield SET_VARIABLE(tmpResultName, resultName)
			resultName = tmpResultName

		for moduleName in moduleNames:
			if moduleName == '.':
				continue

			yield GET_ATTRIBUTE(resultName, resultName, moduleName.name)


@asDecorator(
	lambda rule: executeSyncCoroutine(From.setAttribute('__syntaxRule__', rule))
)
@SyntaxRule.wrap(
	Value(From),
	Token(' '),
	MatchParsed(IsInstance(VARIABLE)),
	Many(Token('.'), MatchParsed(IsInstance(VARIABLE)), minMatches=0),
	Token(' '),
	MatchParsed(Value(import_)),
	Token(' '),
	MatchParsed(Or([IsInstance(VARIABLE)], [Token('*')])),
	useParser=True,
)
def _parseFromImport(*args, parser=None):
	args = BufferRule(parser, Buffer(args))
	args.pop(Value(From), Token(' '))

	codeModuleName = tuple(args.popUntil(Token(' ')))
	args.pop(Token(' '))
	codeModuleImport = Buffer(
		(*args.pop(Value(import_)), ' ', *codeModuleName, *' as ', parser.makeTmpVar())
	)
	codeModuleImport = tuple(parser.subParser(codeModuleImport))
	yield from codeModuleImport
	args.pop(Token(' '))
	moduleVarName = codeModuleImport[-1].dst

	for attributeName in args:
		if '*' == attributeName:
			yield CALL_FUNCTION_STATIC(
				'_', copyAlllIntoScope.call, args=(moduleVarName, '__scope__')
			)
			continue

		yield GET_ATTRIBUTE(attributeName.name, moduleVarName, attributeName.name)
