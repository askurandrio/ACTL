from actl import Parser, Scope, objects
from actl.Buffer import Buffer
from actl.Project import Lazy, importFrom
import std


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



async def import_( name):
	from std.base.objects import Module  # pylint: disable=import-outside-toplevel

	return await Module.call(name=name)


def getImport(_):
	return import_
