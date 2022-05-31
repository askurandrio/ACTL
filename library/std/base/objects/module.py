import os

from actl.objects import makeClass, AToPy, addMethod, AAttributeNotFound, Signature
from actl.Buffer import Buffer
from actl.opcodes.opcodes import RETURN
from std.base.objects.function import Function
from std.base.executor import bindExecutor


Module = makeClass('Module')


@addMethod(Module, '__init__')
async def _Module__init(self, path):
	await self.setAttribute('__path__', path)
	await self.setAttribute('__scope__', None)
	await self.setAttribute('__modules__', {})

	executor = await bindExecutor()
	await self.setAttribute('__project__', executor.scope['__project__'])

	if os.path.isfile(path):
		executeModule = await self.getAttribute('_executeModule')
		await executeModule.call()


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

	if scope is not None:
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


@addMethod(Module, '_executeModule')
async def _Module__executeModule(self):
	path = await self.getAttribute('__path__')
	project = await self.getAttribute('__project__')
	pyProject = AToPy(project)
	parsedInput = None

	@Buffer.wrap
	async def createParsedInput():
		nonlocal parsedInput

		input_ = _open(path)

		executor = await bindExecutor()
		parsedInput = pyProject['parseInput'](executor.scope, input_)

	@Buffer.wrap
	def yieldParsedInput():
		yield from parsedInput
		yield RETURN('__scope__')

	name = f'{self}__executeModuleCode'
	signature = await Signature.call(())
	body = createParsedInput() + yieldParsedInput()
	scope = pyProject['initialScope']
	function = await Function.call(name, signature, body, scope)
	moduleScope = await function.call()
	await self.setAttribute('__scope__', moduleScope)


@Buffer.wrap
def _open(fileName):
	with open(fileName) as file:
		for line in file:
			for char in line:
				yield char
