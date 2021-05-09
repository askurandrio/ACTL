from logging import addLevelName
import os

from actl import Result, DIR_LIBRARY
from actl.Buffer import Buffer
from actl.objects import addMethod, addMethodToClass, makeClass, AAttributeNotFound, AToPy
from actl.opcodes import RETURN


Module = makeClass('Module')


@addMethodToClass(Module, '__call__')
def _Module__call(cls, path=None, name=None):
	if path is not None:
		return cls.super_.obj(Module, '__call__').obj.call.obj(path)

	if '.' not in name:
		path = os.path.join(DIR_LIBRARY, name)
		return cls.call.obj(path)

	packageName = name[:name.find('.')]
	name = name[name.find('.')+1:]

	packageResult = cls.call.obj(name=packageName)

	@packageResult.then
	def result(package):
		resultImport = package.getAttribute.obj('import_').obj.call.obj(name)

		@resultImport.then
		def result(_):
			return package

		return result

	return result


@addMethod(Module, '__init__')
def _Module__init(self, path):
	isPackage = os.path.isdir(path)
	if not isPackage:
		path = f'{path}.a'
	moduleScope = None

	@Result.fromExecute
	def resultExecuteModule(executor):
		nonlocal moduleScope

		project = AToPy(executor.scope['__project__'])
		moduleScope = project['initialScope'].child()
		executor.scope, prevScope = moduleScope, executor.scope

		if not isPackage:
			input_ = _open(path)
			parsedInput = project['parseInput'](moduleScope, input_)
			yield from parsedInput

		try:
			yield RETURN('None')
		except GeneratorExit:
			executor.scope = prevScope

	@resultExecuteModule.then
	def result(_):
		self.setAttribute('scope', moduleScope)
		self.setAttribute('path', path)
		return self

	return result


@addMethod(Module, 'import_')
def _Module__import_(self, name):
	if '.' in name:
		packageName = name[:name.find('.')]
		name = name[name.find('.')+1:]

		packageResult = self.getAttribute.obj('import_').obj.call.obj(packageName)

		@packageResult.then
		def result(_):
			package = self.getAttribute.obj(packageName).obj
			return package.getAttribute.obj('import_').obj.call.obj(name)

		return result

	path = str(self.getAttribute.obj('path').obj)
	path = os.path.join(path, name)

	resultModule = self.class_.call.obj(path)

	@resultModule.then
	def result(module):
		self.setAttribute(name, module)

	return result


@addMethod(Module, '__getAttribute__')
def _Module__getAttribute(self, key):
	resultGetAttribute = self.super_.obj(Module, '__getAttribute__').obj.call.obj(key)

	try:
		return Result.fromObj(resultGetAttribute.obj)
	except AAttributeNotFound(key=key).class_:
		pass

	scope = self.super_.obj(Module, '__getAttribute__').obj.call.obj('scope').obj
	return Result.fromObj(scope[key])


@Buffer.wrap
def _open(fileName):
	with open(fileName) as file:
		for line in file:
			for char in line:
				yield char
