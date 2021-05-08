from actl import asDecorator
from actl.opcodes import CALL_FUNCTION_STATIC, VARIABLE
from actl.syntax import SyntaxRule, Value, Token, IsInstance, Parsed, Many
from actl.objects import addMethodToClass, makeClass
from std.base.objects.module import Module


Import = makeClass('import')


@addMethodToClass(Import, '__call__')
def _Import__call(_, name):
	return Module.call.obj(name=name)


@asDecorator(lambda rule: Import.setAttribute('__syntaxRule__', rule))
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
def _Import__syntaxRule(_, _1, returnVar, *nameVars):
	importName = ''.join(
		(nameVar.name if VARIABLE == nameVar else nameVar)
		for nameVar in (returnVar, *nameVars)
	)
	return [
		CALL_FUNCTION_STATIC(returnVar.name, Import.call.obj, args=[importName])
	]
