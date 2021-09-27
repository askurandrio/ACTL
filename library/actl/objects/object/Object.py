from actl.objects.object.AObject import AObject
from actl.objects.object.exceptions import AAttributeNotFound
from actl.objects.object.utils import addMethod, addMethodToClass, makeClass


Object = makeClass('Object')
AObject.Object = Object


@addMethod(Object, '__getAttribute__')
async def object__getAttribute(self, key):
	attribute, isSuccess = await self.lookupSpecialAttribute(key)
	if isSuccess:
		return attribute

	attribute, isSuccess = self.lookupAttributeInHead(key)
	if isSuccess:
		return attribute

	attribute, isSuccess = self.lookupAttributeInClsSelf(key)
	if isSuccess:
		bindedAttribute = await self.bindAttribute(attribute)
		return bindedAttribute

	raise AAttributeNotFound(key)


@addMethod(Object, '__superGetAttribute__')
async def object__superGetAttribute(self, for_, key):
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
			return await self.bindAttribute(attribute)

	raise AAttributeNotFound(key)


@addMethodToClass(Object, '__call__')
async def Object__call(self, *args, **kwargs):
	assert isinstance(self, AObject)
	instance = AObject({'__class__': self})

	initMethod = await instance.getAttribute('__init__')
	await initMethod.call(*args, **kwargs)

	return instance


@addMethod(Object, '__init__')
async def object__init(_):
	return None
