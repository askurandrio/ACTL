from actl.objects.object.AObject import AObject
from actl.objects.object.class_ import class_
from actl.objects.object.exceptions import AAttributeNotFound
from actl.signals import triggerSignal, onSignal
from actl.utils import executeSyncCoroutine


Object = executeSyncCoroutine(class_.call('Object'))


@Object.addMethod('__getAttribute__')
async def object__getAttribute(self, key):
	attribute, isSuccess = await self.getAttribute.lookupSpecialAttribute(key)
	if isSuccess:
		return attribute

	attribute, isSuccess = self.getAttribute.lookupAttributeInHead(key)
	if isSuccess:
		return attribute

	attribute, isSuccess = await self.getAttribute.lookupAttributeInClsSelf(key)
	if isSuccess:
		bindedAttribute = await self.getAttribute.bind(attribute)
		return bindedAttribute

	raise AAttributeNotFound(key)


@Object.addMethod('__superGetAttribute__')
async def object__superGetAttribute(self, for_, key):
	cls = await self.getAttribute('__class__')
	parents = await cls.getAttribute('__parents__')

	if for_ in parents:
		forIndex = parents.index(for_)
		parents = parents[forIndex + 1 :]

	for parent in parents:
		self_ = await parent.getAttribute('__self__')
		try:
			attribute = self_[key]
		except KeyError:
			pass
		else:
			return await self.getAttribute.bind(attribute)

	raise AAttributeNotFound(key)


@Object.addMethodToClass('__call__')
async def Object__call(self, *args, **kwargs):
	assert isinstance(self, AObject)
	instance = AObject({'__class__': self})

	initMethod = await instance.getAttribute('__init__')
	await initMethod.call(*args, **kwargs)

	return instance


@Object.addMethod('__init__')
async def object__init(_):
	return None


@Object.addMethod('__setAttribute__')
async def object__setAttribute(self, key, value):
	self.head[key] = value


async def _toPyString(self):
	if not hasattr(_toPyString, '_stringSeen'):
		_toPyString._stringSeen = set()

		try:
			return await _toPyString(self)
		finally:
			del _toPyString._stringSeen

	_toPyString._stringSeen.add(id(self))

	cls = await self.getAttribute('__class__')
	name = await cls.getAttribute('__name__')
	selfToStr = f'{name}<'

	for key, value in self.head.items():
		if key == '__class__':
			continue

		if id(value) in _toPyString._stringSeen:
			reprValue = '↑...'
		else:
			_toPyString._stringSeen.add(id(value))
			reprValue = repr(value)

		selfToStr = f'{selfToStr}{key}={reprValue}, '

	if selfToStr[-2:] == ', ':
		selfToStr = selfToStr[:-2]

	return f'{selfToStr}>'


@onSignal('actl.String:created')
async def _onStringCreated(String):
	@Object.addMethod(String)
	async def object__String(self):
		pyString = await _toPyString(self)
		return await String.call(pyString)


executeSyncCoroutine(triggerSignal('actl.Object:created', Object))
