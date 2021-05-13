from actl.objects import NativeFunction, Result
from actl.opcodes import CALL_FUNCTION_STATIC, RETURN
from std.base.objects import Import


@NativeFunction
def inject(project):
	@Result.fromExecute
	def result(executor):
		executor.scope, prevScope = project.this['initialScope'], executor.scope

		yield CALL_FUNCTION_STATIC(
			'_tmpVarTrash',
			Import.call,
			kwargs={'fromName': 'std.std.init', 'importName': '*'}
		)
		try:
			yield RETURN('None')
		except GeneratorExit:
			executor.scope = prevScope

	return result
