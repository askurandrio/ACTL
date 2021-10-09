from actl.Buffer import Buffer
from actl.objects import addMethod, makeClass, AAttributeNotFound, AToPy
from std.base.executor.Executor import Frame
from std.base.executor.utils import bindExecutor


Package = makeClass('Package')
Module = makeClass('Module', parents=(Package,))


@addMethod(Package, '__init__')
async def _Package__init(self, path):
	executor = await bindExecutor()
	project = AToPy(executor.scope['__project__'])
	scope = project['initialScope'].child()
	self.setAttribute('scope', scope)
	self.setAttribute('path', path)


@addMethod(Module, '__init__')
async def _Module__init(self, path):
	superInit = await self.super_(Module, '__init__')
	await superInit.call(path)

	executor = await bindExecutor()
	project = AToPy(executor.scope['__project__'])
	moduleScope = await self.getAttribute('scope')
	executor.scope, prevScope = moduleScope, executor.scope

	input_ = _open(path)
	parsedInput = project['parseInput'](moduleScope, input_)
	await Frame(parsedInput)

	executor.scope = prevScope



@addMethod(Package, '__getAttribute__')
async def _Package__getAttribute(self, key):
	superGetAttribute = await self.super_(Package, '__getAttribute__')

	try:
		return await superGetAttribute.call(key)
	except AAttributeNotFound.class_(key=key):
		pass

	scope = await superGetAttribute.call('scope')

	try:
		return scope[key]
	except KeyError as ex:
		raise AAttributeNotFound(key) from ex


@Buffer.wrap
def _open(fileName):
	with open(fileName) as file:
		for line in file:
			for char in line:
				yield char
