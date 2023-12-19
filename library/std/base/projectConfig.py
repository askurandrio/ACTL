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


def getInitialScope(project):  # pylint: disable=unused-argument
	def lt(first, second):  # pylint: disable=unused-variable
		return first < second

	scope = {}
	loader = _loadFromScope()

	for varName, pyName in (
		('print', 'print'),
		('readInput', 'input'),
		('True', 'objects.Bool.True_'),
		('False', 'objects.Bool.False_'),
		('Bool', 'objects.Bool'),
		('Object', 'objects.Object'),
		('String', 'objects.String'),
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
		('breakPoint', 'breakpoint'),
	):
		pyVar = loader(pyName)
		var = executeSyncCoroutine(objects.PyToA.call(pyVar))
		varCast = executeSyncCoroutine(var.getAttribute('cast'))
		varCastResult = executeSyncCoroutine(varCast.call())
		scope[varName] = varCastResult

	return Scope(scope)


def getParseInput(project):
	def parseInput(scope, input_):
		return Parser(scope, project['rules'], input_)

	return parseInput


def getBuildScope(project):
	return project['initialScope'].child()


def getBuildExecutor(project):
	return std.base.Executor(project['buildScope'])


def getBuild(project):
	def build():
		executor = project['buildExecutor']
		code = project['buildCode']

		executor.execute(code)

	return build


def getLibraryDirectories(project):
	libraryDirectories = [DIR_LIBRARY]

	try:
		mainF = project['mainF']
	except KeyError:
		pass
	else:
		libraryDirectories.append(os.path.dirname(mainF))

	return libraryDirectories


def _cacheInSelf(method):
	async def wrapper(self, *args):
		key = (method, args)
		if key in self.cache:
			return self.cache[key]

		self.cache[key] = await method(self, *args)
		return await wrapper(self, *args)

	return wrapper


class Importer:
	def __init__(self, currentProject):
		self._currentProject = currentProject
		self.cache = {}

	async def importByName(self, name):
		if name in self.cache:
			return self.cache[name]

		if '.' in name:
			moduleNames = name.split('.')
			mainPackageName = moduleNames.pop(0)
			mainPackage = await self.importByName(mainPackageName)
			package = mainPackage
			for (
				moduleName
			) in moduleNames:  # pylint: disable=redefined-argument-from-local
				package = await package.getAttribute(moduleName)

			self.cache[name] = package
			return await self.importByName(name)

		for dirLibrary in self._currentProject['libraryDirectories']:
			path = os.path.join(dirLibrary, name)

			async def onModuleCreated(module):
				self.cache[name] = module

			await self.importByPath(onModuleCreated, path)
			if name in self.cache:
				return await self.importByName(name)

		raise RuntimeError(
			f"Module {name} not found in {self._currentProject}, "
			f"{self._currentProject['libraryDirectories']=}"
		)

	async def importByPath(self, onModuleCreated, path):
		if path in self.cache:
			await onModuleCreated(self.cache[path])
			return

		async def localOnModuleCreated(module):
			self.cache[path] = module
			await onModuleCreated(module)

		executor = await bindExecutor()

		if executor != self._currentProject['buildExecutor']:
			self._currentProject['buildExecutor'].executeCoroutine(
				self._currentProject['import'].importByPath(localOnModuleCreated, path)
			)
			return

		if os.path.isdir(path):
			pathBaseName = os.path.basename(path)
			yamlPath = os.path.join(path, f'{pathBaseName}.yaml')
			if os.path.isfile(yamlPath):
				project = self._currentProject.import_(yamlPath)
				if project is not self._currentProject:
					await project['import'].importByPath(localOnModuleCreated, path)
					return

			await executor.scope['Module'].call(localOnModuleCreated, path)
			return

		aPath = f'{path}.a'
		if os.path.isfile(aPath):
			await executor.scope['Module'].call(localOnModuleCreated, aPath)
			return

		return
