import os

from actl.objects import makeClass, AToPy, addMethod, AAttributeNotFound
from actl.Buffer import Buffer
from std.base.executor import Frame, bindExecutor


Module = makeClass('Module')


@addMethod(Module, '__init__')
async def _Module__init(self, path):
	executor = await bindExecutor()
	project = executor.scope['__project__']
	pyProject = AToPy(project)
	moduleScope = pyProject['initialScope'].child()

	if os.path.isfile(path):
		executor.scope, prevScope = moduleScope, executor.scope

		input_ = _open(path)
		parsedInput = pyProject['parseInput'](moduleScope, input_)
		await Frame(parsedInput)

		executor.scope = prevScope

	self.setAttribute('__path__', path)
	self.setAttribute('__scope__', moduleScope)
	self.setAttribute('__modules__', {})
	self.setAttribute('__project__', project)


@addMethod(Module, '__getAttribute__')
async def _Module__getAttribute(self, key):
	superGetAttribute = await self.super_(Module, '__getAttribute__')

	try:
		return await superGetAttribute.call(key)
	except AAttributeNotFound.class_(key=key):
		pass

	modules = await self.getAttribute('__modules__')

	try:
		return modules[key]
	except KeyError:
		pass

	scope = await superGetAttribute.call('__scope__')

	try:
		return scope[key]
	except KeyError:
		pass

	project = AToPy(await self.getAttribute('__project__'))
	dirLibrary = await self.getAttribute('__path__')
	path = os.path.join(dirLibrary, key)
	module = await project['import'].importByPath(path)

	if module is not None:
		modules[key] = module
		return await self.getAttribute(key)

	raise AAttributeNotFound(key)


@Buffer.wrap
def _open(fileName):
	with open(fileName) as file:
		for line in file:
			for char in line:
				yield char
