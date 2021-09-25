import os

from actl import DIR_LIBRARY
from actl.Buffer import Buffer
from actl.objects import addMethod, addMethodToClass, makeClass, AAttributeNotFound, AToPy
from std.base.executor.Executor import Frame
from std.base.executor.utils import bindExecutor


Module = makeClass('Module')


@addMethodToClass(Module, '__call__')
async def _Module__call(cls, path=None, name=None):
	if path is not None:
		superCall = await cls.super_(Module, '__call__')
		return await superCall.call(path)

	if '.' not in name:
		path = os.path.join(DIR_LIBRARY, name)
		return await cls.call(path)

	packageName = name[:name.find('.')]
	name = name[name.find('.')+1:]

	package = await cls.call(name=packageName)
	importMethod = await package.getAttribute('import_')
	await importMethod.call(name)

	return package


@addMethod(Module, '__init__')
async def _Module__init(self, path):
	isPackage = os.path.isdir(path)
	if not isPackage:
		path = f'{path}.a'

	executor = await bindExecutor()
	project = AToPy(executor.scope['__project__'])
	moduleScope = project['initialScope'].child()
	executor.scope, prevScope = moduleScope, executor.scope

	if not isPackage:
		input_ = _open(path)
		parsedInput = project['parseInput'](moduleScope, input_)
		await Frame(parsedInput)

	executor.scope = prevScope
	self.setAttribute('scope', moduleScope)
	self.setAttribute('path', path)

	return self


@addMethod(Module, 'import_')
async def _Module__import_(self, name):
	if '.' in name:
		subPackageName = name[:name.find('.')]
		moduleName = name[name.find('.')+1:]

		importMethod = await self.getAttribute('import_')
		await importMethod.call(subPackageName)
		subPackage = await self.getAttribute(subPackageName)
		subPackageImportMethod = await subPackage.getAttribute('import_')
		await subPackageImportMethod.call(moduleName)
		return

	path = str(await self.getAttribute('path'))
	path = os.path.join(path, name)

	module = await self.class_.call(path)
	self.setAttribute(name, module)


@addMethod(Module, '__getAttribute__')
async def _Module__getAttribute(self, key):
	superGetAttribute = await self.super_(Module, '__getAttribute__')

	try:
		return await superGetAttribute.call(key)
	except AAttributeNotFound(key=key).class_:
		pass

	scope = await superGetAttribute.call('scope')
	return scope[key]


@Buffer.wrap
def _open(fileName):
	with open(fileName) as file:
		for line in file:
			for char in line:
				yield char
