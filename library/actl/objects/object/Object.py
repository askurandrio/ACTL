from actl.objects.object.AObject import AObject
from actl.objects.object.exceptions import AAttributeIsNotSpecial, AAttributeNotFound
from actl.objects.object.utils import addMethod, addMethodToClass, makeClass


Object = makeClass('Object')
AObject.Object = Object


@addMethod(Object, '__getAttribute__')
async def object__getAttribute(self, key):
	try:
		return await self.lookupSpecialAttribute(key)
	except AAttributeIsNotSpecial(key).class_:
		pass

	try:
		return self.lookupAttributeInHead(key)
	except AAttributeNotFound(key).class_:
		pass

	try:
		attribute = self.lookupAttributeInClsSelf(key)
	except AAttributeNotFound(key).class_:
		pass
	else:
		return await self.bindAttribute(attribute)

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
