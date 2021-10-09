import os

from actl import Parser, Scope, objects
from actl.Buffer import Buffer
from actl.Project import DIR_LIBRARY, Lazy, importFrom
from actl.objects.PyToA import PyToA
import std
from std.base.executor import bindExecutor


def pyExternalKey(project, arg):
	def get():
		value = importFrom(arg)

		return value(project)

	project[arg['name']] = Lazy(get)


def loadHandlerPyExternalKey(project):
	project['handlers']['py-externalKey'] = pyExternalKey


def getRules(_):
	return std.base.RULES


def getInitialScope(project):
	scope = {}
	lt = lambda first, second: first < second

	for varName, pyName in (
		('print', 'print'),
		('readInput', 'input'),
		('True', 'objects.Bool.True_'),
		('False', 'objects.Bool.False_'),
		('Bool', 'objects.Bool'),
		('Object', 'objects.Object'),
		('String', 'objects.String'),
		('Number', 'objects.Number'),
		('elif', 'objects.elif_'),
		('else', 'objects.else_'),
		('None', 'objects.ANone'),
		('PyToA', 'objects.PyToA'),
		('if', 'std.base.objects.If'),
		('while', 'std.base.objects.While'),
		('fun', 'std.base.objects.Function'),
		('class', 'std.base.objects.class_'),
		('import', 'std.base.objects.Import'),
		('from', 'std.base.objects.From'),
		('Module', 'std.base.objects.Module'),
		('Package', 'std.base.objects.Package'),
		('__project__', 'project'),
		('lt', 'lt')
	):
		pyVar = eval(pyName)
		var = objects.executeSyncCoroutine(objects.PyToA.call(pyVar))
		scope[varName] = var

	return Scope(scope)


def getInput(project):
	@Buffer.wrap
	def make():
		for line in open(project['mainF']):
			for char in line:
				yield char

	return make()


def getParseInput(project):
	def parseInput(scope, input_):
		return Parser(scope, project['rules'], input_)

	return parseInput


def getBuildScope(project):
	return project['initialScope'].child()


def getBuildParser(project):
	return project['parseInput'](
		project['buildScope'], project['input']
	)


def getBuildExecutor(project):
	return std.base.Executor(
		project['buildParser'], project['buildScope']
	)


def getBuild(project):
	def build():
		project['buildExecutor'].execute()

	return build


def getLibraryDirectory(project):
	projectF = project['projectF']
	return os.path.dirname(projectF)


class Importer:
	def __init__(self, currentProject):
		self._currentProject = currentProject
		self._cache = {}

	async def __call__(self, name=None, path=None):
		key = (name, path)

		if key in self._cache:
			return self._cache[key]

		self._cache[key] = await self._call(name=name, path=path)
		return await self(name=name, path=path)

	async def getProjectPackage(self):
		projectF = self._currentProject['projectF']
		return await self(path=os.path.dirname(projectF))

	async def _call(self, name, path):
		if path is not None:
			return await self._importPath(path)

		if '.' in name:
			return await self._importPackage(name)

		for dirLibrary in self._getLibraryDirs():
			path = os.path.join(dirLibrary, name)
			if os.path.isdir(path) or os.path.isfile(f'{path}.a'):
				return await self(path=path)

		raise RuntimeError(f'Module {name} not found')

	def _getLibraryDirs(self):
		yield DIR_LIBRARY

		try:
			yield self._currentProject['libraryDirectory']
		except KeyError:
			return

	async def _importPackage(self, name):
		names = name.split('.')
		moduleName = names.pop(-1)
		mainPackage = await self('.'.join(names))
		package = mainPackage

		for subModuleName in names[1:]:
			package = await package.getAttribute(subModuleName)

		if await package.hasAttribute(moduleName):
			return mainPackage

		if await package.hasAttribute('__forProject__'):
			project = objects.AToPy(await package.getAttribute('__forProject__'))
			module = await project['import'](moduleName)
		else:
			packagePath = await package.getAttribute('path')
			modulePath = os.path.join(packagePath, moduleName)
			module = await self(path=modulePath)

		package.setAttribute(moduleName, module)

		return mainPackage

	async def _importPath(self, path):
		executor = await bindExecutor()

		if os.path.isdir(path):
			pathBaseName = os.path.basename(path)
			yamlPath = os.path.join(path, f'{pathBaseName}.yaml')
			if os.path.isfile(yamlPath):
				project = self._currentProject.loadProject(yamlPath)
				if project != self._currentProject:
					return await project['import'].getProjectPackage()

				package = await executor.scope['Package'].call(path)
				aProject = await PyToA.call(self._currentProject)
				package.setAttribute('__forProject__', aProject)
				return package

			return await executor.scope['Package'].call(path)

		path = f'{path}.a'
		return await executor.scope['Module'].call(path)
