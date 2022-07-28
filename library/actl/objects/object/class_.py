from re import A
from actl.objects.object.AObject import AObject
from actl.objects.object.NativeMethod import NativeFunction
from actl.objects.object.exceptions import AAttributeNotFound
from actl.objects.object.NativeMethod import NativeMethod
from actl.utils import executeSyncCoroutine
from actl.signals import onSignal


_Object = None


class AObjectClass(AObject):
	def addMethod(self, name):
		def decorator(function):
			aFunction = NativeFunction(function)
			self_ = executeSyncCoroutine(self.getAttribute('__self__'))
			self_[name] = aFunction
			return function

		return decorator

	def addMethodToClass(self, name):
		def decorator(function):
			aFunction = NativeMethod(function)
			self.head[name] = aFunction

		return decorator


@onSignal('actl.Object:created', None)
async def _onObjectCreated(Object):
	global _Object

	_Object = Object


@NativeFunction
async def class__call(
	cls, name, parents=(), baseParent=None, self_=None, extraAttributes=None
):
	baseParent = baseParent or _Object
	if baseParent is not None:
		parents = [*parents, _Object]

	while (len(parents) > 1) and (parents[-1] == parents[-2]):
		parents.pop(-1)

	self_ = {} if self_ is None else self_
	extraAttributes = {} if extraAttributes is None else extraAttributes

	return AObjectClass(
		{
			'__name__': name,
			'__class__': cls,
			'__parents__': parents,
			'__self__': self_,
			**extraAttributes,
		}
	)


@NativeFunction
async def class__getAttribute(self, key):
	attribute, isSuccess = await self.getAttribute.lookupSpecialAttribute(key)
	if isSuccess:
		return attribute

	attribute, isSuccess = self.getAttribute.lookupAttributeInHead(key)
	if isSuccess:
		bindedAttribute = await self.getAttribute.bind(attribute)
		return bindedAttribute

	attribute, isSuccess = await self.getAttribute.lookupAttributeInClsSelf(key)
	if isSuccess:
		bindedAttribute = await self.getAttribute.bind(attribute)
		return bindedAttribute

	for parent in await self.getAttribute('__parents__'):
		if isinstance(parent, str):
			assert False, parent

		attribute, isSuccess = parent.getAttribute.lookupAttributeInHead(key)
		if isSuccess:
			bindedAttribute = await self.getAttribute.bind(attribute)
			return bindedAttribute

	raise AAttributeNotFound(key)


@NativeFunction
async def class__superGetAttribute(self, for_, key):
	parents = await self.getAttribute('__parents__')

	if for_ in parents:
		forIndex = parents.index(for_)
		parents = parents[forIndex + 1 :]

	for parent in parents:
		attribute, isSucess = parent.getAttribute.lookupAttributeInHead(key)
		if isSucess:
			bindedAttribute = await self.getAttribute.bind(attribute)
			return bindedAttribute

	raise AAttributeNotFound(key)


@NativeFunction
async def class__setAttribute(self, key, value):
	self.head[key] = value


class_ = AObjectClass(
	{
		'__name__': 'class',
		'__parents__': (),
		'__self__': {
			'__getAttribute__': class__getAttribute,
			'__setAttribute__': class__setAttribute,
			'__superGetAttribute__': class__superGetAttribute,
		},
	}
)

class_.head['__class__'] = class_
class_.head['__getAttribute__'] = executeSyncCoroutine(
	class__getAttribute.apply(class_)
)
class_.head['__call__'] = class__call


@onSignal('actl.String:created')
async def _onStringCreated(String):
	@class_.addMethod(String)
	async def class__String(self):
		name = await self.getAttribute('__name__')
		return await String.call(f"class '{name}'")
