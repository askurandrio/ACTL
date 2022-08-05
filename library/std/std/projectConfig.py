from actl.Scope import ScopeChild
from actl import opcodes, executeSyncCoroutine
from actl.objects import NativeFunction, PyToA

from std.base import Executor
from std.base.projectConfig import getInitialScope as getInitialBaseScope
from std.base.objects.importDefinition import import_, copyAlllIntoScope
from std.base.objects import If


def getInitialScope(project):
	if not project['projectF'].endswith('ACTL/library/std/std/std.yaml'):
		return project['std']['initialScope'].child()

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
					opcodes.GET_ATTRIBUTE('main', 'module', 'main'),
					opcodes.CALL_FUNCTION_STATIC('_', 'main'),
				],
			]
		)
	)
	yield ifOpcode


@NativeFunction
async def _hasAttribute(obj, attribute):
	hasAttribute = await obj.hasAttribute(attribute)
	return await PyToA.call(hasAttribute)
