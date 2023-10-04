# pylint: disable=protected-access
from actl.objects.object import Object, class_, AObject, AObjectClass
from actl.signals import triggerSignal, onSignal
from actl.utils import executeSyncCoroutine


class _AStringClass(AObjectClass):
	def __str__(self):
		return "class 'String'"


class _AString(AObject):
	def __init__(self, head, value):
		super().__init__(head)
		self.value = value


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
			value = value.value
		else:
			toStringMethod = await value.getAttribute(String)
			return await toStringMethod.call()

	self = _AString({'__class__': cls}, value)
	return self


@onSignal('actl.PyToA:created')
async def _onPyToACreated(PyToA):
	@String.addMethod(PyToA)
	async def string_PyToA(self):
		return await PyToA.call(self.value)


executeSyncCoroutine(triggerSignal('actl.String:created', String))


@String.addMethod(String)
async def sting__String(self):
	return self


@onSignal('actl.Number:created')
async def _onNumberCreated(Number):
	@String.addMethod(Number)
	async def string__Number(self):
		value = float(self.value)
		return await Number.call(value)
