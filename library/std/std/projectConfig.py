from std.base import Executor
from std.base.projectConfig import getInitialScope as getInitialBaseScope
from std.base.objects.importDefinition import import_, copyAlllIntoScope
from actl.Scope import ScopeChild


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
