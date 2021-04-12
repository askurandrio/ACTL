from actl.Result import Result
from actl.objects.object.AObject import AObject
from actl.objects.object.exceptions import AAttributeIsNotSpecial, AAttributeNotFound
from actl.objects.object.utils import addMethod, addMethodToClass, makeClass


Object = makeClass('Object')
makeClass.Object = Object


@addMethod(Object, '__getAttribute__')
def object__getAttribute(self, key):
	try:
		return Result(obj=self.lookupSpecialAttribute(key))
	except AAttributeIsNotSpecial(key).class_:
		pass

	try:
		return Result(obj=self.lookupAttributeInHead(key))
	except AAttributeNotFound(key).class_:
		pass

	try:
		attribute = self.lookupAttributeInClsSelf(key)
	except AAttributeNotFound(key).class_:
		pass
	else:
		return self.bindAttribute(attribute)

	raise AAttributeNotFound(key)


@addMethod(Object, '__superGetAttribute__')
def object__superGetAttribute(self, for_, key):
	class_ = self.class_
	parents = class_.parents

	if for_ in parents:
		forIndex = parents.index(for_)
		parents = parents[forIndex:]

	for parent in parents:
		self_ = parent.self_
		try:
			attribute = self_[key]
		except KeyError:
			pass
		else:
			return self.bindAttribute(attribute)

	raise AAttributeNotFound(key)


@addMethodToClass(Object, '__call__')
def Object__call(self, *args, **kwargs):
	assert not isinstance(self, Result)
	instance = AObject({'__class__': self})

	resultInstanceGetAttribute = instance.getAttribute

	@resultInstanceGetAttribute.then
	def resultInitMethod(instanceGetAttribute):
		return instanceGetAttribute('__init__')

	@resultInitMethod.then
	def resultInitMethodFunc(initMethod):
		return initMethod.call

	@resultInitMethodFunc.then
	def resultInitMethodCall(initMethodFunc):
		initMethodFunc(*args, **kwargs)

	@resultInitMethodCall.then
	def resultInstance(_):
		return instance

	return resultInstance


@addMethod(Object, '__init__')
def object__init(_):
	return Result(obj=None)
