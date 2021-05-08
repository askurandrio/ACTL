import os

from actl import Result, DIR_LIBRARY, asDecorator
from actl.Buffer import Buffer
from actl.opcodes import CALL_FUNCTION_STATIC, RETURN, VARIABLE
from actl.syntax import SyntaxRule, Value, Token, IsInstance
from actl.objects import addMethodToClass, AToPy, makeClass
from std.base.objects.Module import Module


import_ = makeClass('import')


@addMethodToClass(import_, '__call__')
def _import__call(_, name):
	@Result.fromExecute
	def result(executor):
		project = AToPy(executor.scope['__project__'])
		moduleScope = project['initialScope'].child()
		moduleScope['__module__'] = Module.call.obj(moduleScope).obj
		input_ = _open(os.path.join(DIR_LIBRARY, f'{name}.a'))
		parsedInput = project['parseInput'](moduleScope, input_)
		executor.scope, prevScope = moduleScope, executor.scope

		try:
			yield from parsedInput
			yield RETURN('__module__')
		finally:
			executor.scope = prevScope

	return result


@asDecorator(lambda rule: import_.setAttribute('__syntaxRule__', rule))
@SyntaxRule.wrap(
	Value(import_),
	Token(' '),
	IsInstance(VARIABLE)
)
def _import__syntaxRule(_, _1, nameVar):
	return [
		CALL_FUNCTION_STATIC(nameVar.name, import_.call.obj, args=[nameVar.name])
	]


@Buffer.wrap
def _open(fileName):
	with open(fileName) as file:
		for line in file:
			for char in line:
				yield char
