import inspect
import os
import builtins

from actl import (
	Parser,
	Scope,
	objects,
	DIR_LIBRARY,
	importFrom,
	Lazy,
	executeSyncCoroutine,
)
from actl.Buffer import Buffer
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


def _loadFromScope():
	frame = inspect.currentframe().f_back
	scope = {**vars(builtins), **frame.f_globals, **frame.f_locals}

	def loader(key):
		names = key.split('.')
		result = scope[names.pop(0)]

		for name in names:
			result = getattr(result, name)

		return result

	return loader


def getInitialScope(project):
	scope = {}
	lt = lambda first, second: first < second
	loader = _loadFromScope()

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
		('import', 'std.base.objects.import_'),
		('from', 'std.base.objects.From'),
		('Module', 'std.base.objects.Module'),
		('__project__', 'project'),
		('lt', 'lt'),
		('pass', 'None'),
	):
		pyVar = loader(pyName)
		var = executeSyncCoroutine(objects.PyToA.call(pyVar))
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
	return project['parseInput'](project['buildScope'], project['input'])


def getBuildExecutor(project):
	return std.base.Executor(project['buildScope'])


def getBuild(project):
	def build():
		executor = project['buildExecutor']
		code = project['buildParser']
		executor.execute(code)

	return build


def getLibraryDirectory(project):
	try:
		projectF = project['projectF']
	except KeyError:
		return None

	return os.path.dirname(projectF)


def _cacheInSelf(method):
	async def wrapper(self, *args):
		key = (method, args)
		if key in self._cache:
			return self._cache[key]

		self._cache[key] = await method(self, *args)
		return await wrapper(self, *args)

	return wrapper


class Importer:
	def __init__(self, currentProject):
		self._currentProject = currentProject
		self._cache = {}

	@_cacheInSelf
	async def importByName(self, name):
		if '.' in name:
			names = name.split('.')
			mainPackageName = names.pop(0)
			mainPackage = await self.importByName(mainPackageName)
			package = mainPackage
			for name in names:
				package = await package.getAttribute(name)

			return await self.importByName(name)

		for dirLibrary in self._getLibraryDirs():
			path = os.path.join(dirLibrary, name)
			module = await self.importByPath(path)
			if module is not None:
				return module

		raise RuntimeError(f'Module {name} not found in {self._currentProject}')

	def _getLibraryDirs(self):
		yield DIR_LIBRARY

		try:
			yield self._currentProject['libraryDirectory']
		except KeyError:
			return

	@_cacheInSelf
	async def importByPath(self, path):
		executor = await bindExecutor()

		if executor != self._currentProject['buildExecutor']:
			return self._currentProject['buildExecutor'].executeCoroutine(
				self._currentProject['import'].importByPath(path)
			)

		if os.path.isdir(path):
			pathBaseName = os.path.basename(path)
			yamlPath = os.path.join(path, f'{pathBaseName}.yaml')
			if os.path.isfile(yamlPath):
				project = self._currentProject.loadProject(yamlPath)
				if project is self._currentProject:
					return await executor.scope['Module'].call(path)

				return await project['import'].importByPath(path)

			return await executor.scope['Module'].call(path)

		path = f'{path}.a'
		if os.path.isfile(path):
			return await executor.scope['Module'].call(path)

		return None
