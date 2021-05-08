import os

from actl import Result, DIR_LIBRARY, asDecorator
from actl.Buffer import Buffer
from actl.Project import importFrom
from actl.opcodes import CALL_FUNCTION_STATIC, RETURN, VARIABLE
from actl.syntax import SyntaxRule, Value, Token, IsInstance, Parsed, Many
from actl.objects import addMethodToClass, AToPy, makeClass
from std.base.objects.Module import Module


Import = makeClass('import')


@addMethodToClass(Import, '__call__')
def _Import__call(_, importName, dirLibrary=None):
	if dirLibrary is None:
		dirLibrary = DIR_LIBRARY

	if '.' in importName:
		packageName = importName[:importName.rfind('.')]
		importName = importName[importName.rfind('.')+1:]

		packageResult = Import.call.obj(packageName, dirLibrary=dirLibrary)

		@packageResult.then
		def result(package):
			packagePath = AToPy(package.getAttribute.obj('path').obj)
			importResult = Import.call.obj(importName, dirLibrary=packagePath)

			@importResult.then
			def result(module):
				package.setAttribute(importName, module)
				return package

			return result

		return result

	importPath = os.path.join(dirLibrary, importName)
	isPackage = os.path.isdir(importPath)
	if not isPackage:
		importPath = f'{importPath}.a'

	@Result.fromExecute
	def result(executor):
		project = AToPy(executor.scope['__project__'])
		moduleScope = project['initialScope'].child()
		moduleScope['__module__'] = Module.call.obj(importPath, moduleScope).obj
		executor.scope, prevScope = moduleScope, executor.scope

		if not isPackage:
			input_ = _open(importPath)
			parsedInput = project['parseInput'](moduleScope, input_)
			yield from parsedInput

		try:
			yield RETURN('__module__')
		except GeneratorExit:
			executor.scope = prevScope

	return result


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


@Buffer.wrap
def _open(fileName):
	with open(fileName) as file:
		for line in file:
			for char in line:
				yield char
