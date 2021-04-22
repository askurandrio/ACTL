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


def getScope(_):
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
		('class', 'std.base.objects.class_')
	):
		pyVar = eval(pyName)
		var = objects.PyToA.call.obj(pyVar).obj
		scope[varName] = var

	return Scope(scope)


def getInput(project):
	@Buffer.wrap
	def make():
		for line in open(project.this['mainF']):
			for char in line:
				yield char

	return make()


def getParser(project):
	return Parser(project.this['scope'], project.this['rules'], project.this['input'])


def getExecutor(project):
	return std.base.Executor(project.this['parser'], project.this['scope'])


def getBuild(project):
	def build():
		project.this['executor'].execute()

	return build
