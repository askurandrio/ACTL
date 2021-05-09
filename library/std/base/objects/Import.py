from actl.Result import Result
from actl.opcodes import CALL_FUNCTION_STATIC, VARIABLE
from actl.opcodes.opcodes import RETURN
from actl.syntax import SyntaxRule, Value, Token, IsInstance, Parsed, Many, Or, End
from actl.objects import addMethodToClass, makeClass
from actl.utils import asDecorator
from std.base.objects.module import Module


Import = makeClass('import')
From = makeClass('From')


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
			nonlocal module

			if '.' in fromName:
				for moduleName in fromName.split('.')[1:]:
					module = module.getAttribute.obj(moduleName).obj

			for key, value in module.getAttribute.obj('scope').obj.getDiff():
				executor.scope[key] = value

			yield RETURN('None')

		return result

	return result


@asDecorator(lambda rule: Import.setAttribute('__syntaxRule__',  rule))
@SyntaxRule.wrap(
	Value(Import),
	Token(' '),
	IsInstance(VARIABLE),
	Many(
		Token('.'),
		Parsed(Or([IsInstance(VARIABLE)], [End]), checkEndLineInBuff=True),
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


@asDecorator(lambda rule: From.setAttribute('__syntaxRule__',  rule))
@SyntaxRule.wrap(
	Value(From),
	Token(' '),
	Parsed(Or([IsInstance(VARIABLE)], [End]), checkEndLineInBuff=True),
	IsInstance(VARIABLE),
	Many(
		Token('.'),
		Parsed(Or([IsInstance(VARIABLE)], [End]), checkEndLineInBuff=True),
		IsInstance(VARIABLE),
		minMatches=0
	),
	Token(' '),
	Parsed(Or([IsInstance(VARIABLE)], [End]), checkEndLineInBuff=True),
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
