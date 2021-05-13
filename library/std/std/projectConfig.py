from actl.opcodes import CALL_FUNCTION_STATIC
from std.std.inject import inject


def getInitialScope(project):
	return project['std/base']['initialScope'].child()


def getBuildExecutor(project):
	executor = project['std/base', 'buildExecutor']
	executor.frames.append(iter([
		CALL_FUNCTION_STATIC('_tmpVarTrash', inject.call,	args=[project])
	]))

	return executor
