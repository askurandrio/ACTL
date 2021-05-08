from actl import Result
from actl.objects import addMethod, makeClass, AAttributeNotFound


Module = makeClass('Module')


@addMethod(Module, '__init__')
def _Module__init(self, scope):
	self.setAttribute('scope', scope)

	return Result.fromObj(None)


@addMethod(Module, '__getAttribute__')
def _Module__getAttribute(self, key):
	resultGetAttribute = self.super_.obj(Module, '__getAttribute__').obj.call.obj(key)

	try:
		return Result.fromObj(resultGetAttribute.obj)
	except AAttributeNotFound(key=key).class_:
		pass

	scope = self.super_.obj(Module, '__getAttribute__').obj.call.obj('scope').obj
	return Result.fromObj(scope[key])
