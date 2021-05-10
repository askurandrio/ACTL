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
	project['handlers', 'py-externalKey'] = pyExternalKey


def getRules(_):
	return std.base.RULES


def getInitialScope(project):
	scope = {}
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
		('pyEval', 'eval'),
		('__project__', 'project.this')
	):
		pyVar = eval(pyName)
		var = objects.PyToA.call(pyVar).obj
		scope[varName] = var

	return Scope(scope)


def getInput(project):
	@Buffer.wrap
	def make():
		for line in open(project.this['mainF']):
			for char in line:
				yield char

	return make()


def getParseInput(project):
	def parseInput(scope, input_):
		return Parser(scope, project.this['rules'], input_)

	return parseInput


def getBuildScope(project):
	return project.this['initialScope'].child()


def getBuildParser(project):
	return project.this['parseInput'](
		project.this['buildScope'], project.this['input']
	)


def getBuildExecutor(project):
	return std.base.Executor(
		project.this['buildParser'], project.this['buildScope']
	)


def getBuild(project):
	def build():
		project.this['buildExecutor'].execute()

	return build
