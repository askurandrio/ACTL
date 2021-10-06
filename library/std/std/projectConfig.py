from actl.opcodes import CALL_FUNCTION_STATIC
from std.base import Executor
from std.base.objects import Import


def getInitialScope(project):
	initialScope = project['std/_std']['initialScope'].child()
	type(initialScope).allowOverride = True
	project['initialScope'] = initialScope

	Executor(
		iter([
			CALL_FUNCTION_STATIC(
				'_tmpVarTrash',
				Import.call,
				kwargs={'fromName': 'std.std.init', 'importName': '*'}
			)
		]),
		initialScope
	).execute()

	del project['initialScope']

	type(initialScope).allowOverride = False
	return initialScope
