# pylint: disable=protected-access
from actl.objects.object import Object, class_, AObject, AObjectClass
from actl.signals import triggerSignal
from actl.utils import executeSyncCoroutine


class _AString(AObjectClass):
	async def toPyString(self):
		return self._value


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
		toStringMethod = await value.getAttribute(String)
		return await toStringMethod.call()

	self = _AString({'__class__': cls})
	self._value = str(value)
	return self


executeSyncCoroutine(triggerSignal('actl.String:created', String))
