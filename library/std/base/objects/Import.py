from actl.opcodes import CALL_FUNCTION_STATIC, VARIABLE
from actl.opcodes.opcodes import RETURN
from actl.syntax import SyntaxRule, Value, Token, IsInstance, Parsed, Many, Or, End
from actl.objects import addMethodToClass, makeClass
from actl.utils import ResolveException, asDecorator, ReturnException
from std.base.objects.module import Module


Import = makeClass('import')
From = makeClass('From')


@addMethodToClass(Import, '__call__')
def _Import__call(cls, fromName=None, importName=None):
	if fromName is None:
		return Module.call(name=importName)

	packageResult = cls.call(importName=fromName)

	@packageResult.thenExecute
	def result(executor, module):
		if '.' in fromName:
			for moduleName in fromName.split('.')[1:]:
				module = module.getAttribute(moduleName)

		for key, value in module.getAttribute('scope').getDiff():
			if importName != '*':
				if key != importName:
					continue

			executor.scope[key] = value

		try:
			yield RETURN('None')
		except ResolveException:
			pass

		raise ReturnException(module)

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
		CALL_FUNCTION_STATIC(returnVar.name, Import.call, kwargs={'importName': importName})
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
	Token(' '),
	Parsed(Or([IsInstance(VARIABLE)], [Token('*')]), checkEndLineInBuff=True),
	Or([IsInstance(VARIABLE)], [Token('*')])
)
def _parseFromImport(*args):
	_, _1, *nameVars, _2, _3, _4, importName = args
	fromName = ''.join(
		(nameVar.name if VARIABLE == nameVar else nameVar)
		for nameVar in nameVars
	)
	importName = (importName.name if VARIABLE == importName else importName)
	return [
		CALL_FUNCTION_STATIC(
			'_tmpVarTrash',
			Import.call,
			kwargs={'fromName': fromName, 'importName': importName}
		)
	]
