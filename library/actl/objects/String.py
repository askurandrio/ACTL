# pylint: disable=protected-access
from actl.objects.object import Object, class_, AObject, AObjectClass
from actl.signals import triggerSignal, onSignal
from actl.utils import executeSyncCoroutine


class _AStringClass(AObjectClass):
	def __str__(self):
		return "class 'String'"


String = _AStringClass(
	{
		'__name__': 'String',
		'__class__': class_,
		'__parents__': (Object,),
		'__self__': {},
	}
)


@String.addMethodToClass('__call__')
async def String__call(cls, value=''):
	if isinstance(value, AObject):
		if await String.isinstance_(value):
			value = value._value
		else:
			toStringMethod = await value.getAttribute(String)
			return await toStringMethod.call()

	parentCall = await cls.super_(String, '__call__')
	self = await parentCall.call()
	self._value = str(value)
	return self


@String.addMethod('toPyString')
async def string__toPyString(self):
	return self._value


@onSignal('actl.PyToA:created')
async def _onPyToACreated(PyToA):
	@String.addMethod(PyToA)
	async def string_PyToA(self):
		toPyStringMethod = await self.getAttribute('toPyString')
		pyString = await toPyStringMethod.call()
		return await PyToA.call(pyString)


executeSyncCoroutine(triggerSignal('actl.String:created', String))


@String.addMethod(String)
async def sting__String(self):
	return self


@onSignal('actl.Number:created')
async def _onNumberCreated(Number):
	@String.addMethod(Number)
	async def string__Number(self):
		value = float(self._value)
		return await Number.call(value)
