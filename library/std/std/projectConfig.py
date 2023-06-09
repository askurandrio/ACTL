from actl.Scope import ScopeChild
from actl import opcodes, executeSyncCoroutine
from actl.objects import NativeFunction, PyToA, AToPy

from std.std.rules import RULES
from std.base import Executor, bindExecutor
from std.base.projectConfig import getInitialScope as getInitialBaseScope
from std.base.objects.importDefinition import import_, copyAlllIntoScope
from std.base.objects import If


def getRules(_):
	return RULES


def getInitialScope(project):
	try:
		return project['__initialScope']
	except KeyError:
		pass

	initialScope = getInitialBaseScope(project)
	project['__initialScope'] = initialScope
	ScopeChild.allowOverride = True
	executor = Executor(project['__initialScope'])
	initModule = executor.executeCoroutine(import_.call('std.std.init'))
	executor.executeCoroutine(copyAlllIntoScope.call(initModule, initialScope))

	del project['__initialScope']
	ScopeChild.allowOverride = False

	return initialScope


def getBuildCode(project):
	yield opcodes.CALL_FUNCTION_STATIC(
		'module', 'Module', staticArgs=[project['mainF']]
	)
	ifOpcode = executeSyncCoroutine(
		If.call(
			[
				[
					opcodes.CALL_FUNCTION_STATIC(
						'hasMain',
						_hasAttribute.call,
						kwargs={'obj': 'module'},
						staticKwargs={'attribute': 'main'},
					),
					opcodes.VARIABLE('hasMain'),
				],
				[
					opcodes.CALL_FUNCTION_STATIC('argv', _loadArgv.call),
					opcodes.GET_ATTRIBUTE('main', 'module', 'main'),
					opcodes.CALL_FUNCTION('_', 'main', args='argv'),
				],
			]
		)
	)
	yield ifOpcode


@NativeFunction
async def _hasAttribute(obj, attribute):
	pyHasAttribute = await obj.hasAttribute(attribute)
	hasAttribute = await PyToA.call(pyHasAttribute)
	hasAttributeCastMethod = await hasAttribute.getAttribute('cast')
	hasAttributeCast = await hasAttributeCastMethod.call()
	return hasAttributeCast


@NativeFunction
async def _loadArgv():
	executor = await bindExecutor()
	project = AToPy(executor.scope['__project__'])
	argv = project['argv']

	result = await executor.scope['Vector'].call()
	resultAppend = await result.getAttribute('append')

	for arg in argv:
		aArg = await executor.scope['String'].call(arg)
		await resultAppend.call(aArg)

	return result
