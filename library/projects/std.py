from actl import Parser, Scope, objects
from actl.Buffer import Buffer
from actl.Project import Lazy, importFrom
import std


def pyExternalKey(project, arg):
	def get():
		value = importFrom(arg)

		if arg.get('rawUse'):
			return value
		return value(project)

	project[arg['name']] = Lazy(get)


def loadHandlerPyExternalKey(project):
	project['handlers', 'py-externalKey'] = pyExternalKey


def getRules(_):
	return std.RULES


def getScope(_):
	def _getPyToAVars():
		for varName in ('print',):
			var = eval(varName)
			yield varName, objects.PyToA.call(var)

	def _getACTLVars():
		for varName, clsName in (
			('True', 'ATrue'), ('False', 'AFalse'), ('Bool', 'Bool'), ('String', 'String'),
			('Number', 'Number'), ('elif', 'elif_'), ('else', 'else_'), ('None', 'ANone'),
			('PyToA', 'PyToA')):
			var = getattr(objects, clsName)
			yield varName, var

	def _getSTDVars():
		for varName, clsName in (('if', 'If'), ('while', 'While'), ('def', 'Function')):
			var = getattr(std.objects, clsName)
			yield varName, var

	return Scope({**dict(_getPyToAVars()), **dict(_getACTLVars()), **dict(_getSTDVars())})


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
	project.this['code'] = project.this['parser']
	return std.Executor(project.this['code'], project.this['scope'])


def getBuild(project):
	def build():
		project.this['executor'].execute()

	return build
