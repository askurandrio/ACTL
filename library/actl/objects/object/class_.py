from actl.objects.object.AObject import AObject
from actl.objects.object.NativeMethod import NativeFunction, NativeMethod
from actl.objects.object.exceptions import AAttributeNotFound


async def class__getAttribute(self, key):
	attribute, isSuccess = await self.lookupSpecialAttribute(key)
	if isSuccess:
		return attribute

	attribute, isSuccess = self.lookupAttributeInHead(key)
	if isSuccess:
		bindedAttribute = await self.bindAttribute(attribute)
		return bindedAttribute

	attribute, isSuccess = self.lookupAttributeInClsSelf(key)
	if isSuccess:
		bindedAttribute = await self.bindAttribute(attribute)
		return bindedAttribute

	for parent in self.parents:
		attribute, isSuccess = parent.lookupAttributeInHead(key)
		if isSuccess:
			bindedAttribute = await self.bindAttribute(attribute)
			return bindedAttribute

	raise AAttributeNotFound(key)


async def class__superGetAttribute(self, for_, key):
	parents = await self.getAttribute('__parents__')

	if for_ in parents:
		forIndex = parents.index(for_)
		parents = parents[forIndex + 1 :]

	for parent in parents:
		attribute, isSucess = parent.lookupAttributeInHead(key)
		if isSucess:
			bindedAttribute = await self.bindAttribute(attribute)
			return bindedAttribute

	raise AAttributeNotFound(key)


class_ = AObject(
	{
		'__name__': 'class',
		'__parents__': (),
		'__self__': {
			'__getAttribute__': NativeMethod(class__getAttribute),
			'__superGetAttribute__': NativeMethod(class__superGetAttribute),
		},
	}
)
class_.setAttribute('__class__', class_)
class_.setAttribute(
	'__getAttribute__', NativeFunction(class__getAttribute).apply(class_)
)
