from actl.Result import Result
from actl.opcodes import CALL_FUNCTION_STATIC, VARIABLE
from actl.opcodes.opcodes import RETURN
from actl.syntax import SyntaxRule, Value, Token, IsInstance, Parsed, Many
from actl.objects import addMethodToClass, makeClass
from std.base.objects.module import Module


Import = makeClass('import')


@addMethodToClass(Import, '__call__')
def _Import__call(cls, fromName=None, importName=None):
	if fromName is None:
		return Module.call.obj(name=importName)

	moduleResult = cls.call.obj(importName=fromName)
	assert importName == '*'

	@moduleResult.then
	def result(module):
		@Result.fromExecute
		def result(executor):
			for key, value in module.getAttribute.obj('scope').obj.getDiff():
				executor.scope[key] = value

			yield RETURN('None')

		return result

	return result


@SyntaxRule.wrap(
	Value(Import),
	Token(' '),
	IsInstance(VARIABLE),
	Parsed(),
	Many(
		Token('.'),
		IsInstance(VARIABLE),
		minMatches=0
	)
)
def _parseImport(_, _1, returnVar, *nameVars):
	importName = ''.join(
		(nameVar.name if VARIABLE == nameVar else nameVar)
		for nameVar in (returnVar, *nameVars)
	)
	return [
		CALL_FUNCTION_STATIC(returnVar.name, Import.call.obj, kwargs={'importName': importName})
	]


@SyntaxRule.wrap(
	Token([VARIABLE('from'), ' ']),
	IsInstance(VARIABLE),
	Many(
		Token('.'),
		IsInstance(VARIABLE),
		minMatches=0
	),
	Token(' '),
	Value(Import),
	Token(' *')
)
def _parseFromImport(*args):
	_, _1, *nameVars, _2, _3, _4, importName = args
	fromName = ''.join(
		(nameVar.name if VARIABLE == nameVar else nameVar)
		for nameVar in nameVars
	)
	return [
		CALL_FUNCTION_STATIC(
			'_tmpVarTrash',
			Import.call.obj,
			kwargs={'fromName': fromName, 'importName': importName}
		)
	]


Import.setAttribute('__syntaxRule__', [_parseFromImport, _parseImport])
