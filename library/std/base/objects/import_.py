import os

from actl import Result, DIR_LIBRARY, asDecorator
from actl.Buffer import Buffer
from actl.opcodes import CALL_FUNCTION_STATIC, RETURN, VARIABLE
from actl.syntax import SyntaxRule, Value, Token
from actl.objects import addMethodToClass, AToPy, makeClass
from actl.syntax.CustomTemplate import IsInstance


import_ = makeClass('import')


@addMethodToClass(import_, '__call__')
def _import__call(_, name):
	@Result.fromExecute
	def result(executor):
		project = AToPy(executor.scope['__project__'])
		moduleScope = project['initialScope'].child()
		input_ = _open(os.path.join(DIR_LIBRARY, f'{name}.a'))
		parsedInput = project['parseInput'](moduleScope, input_)
		executor.scope, prevScope = moduleScope.child(), executor.scope

		try:
			yield from parsedInput
			yield RETURN('__scope__')
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
