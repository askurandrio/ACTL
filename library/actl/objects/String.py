# pylint: disable=protected-access
from actl.objects.object import Object, class_
from actl.objects.object.utils import addMethodToClass


class _AString(type(Object)):
	async def toPyString(self):
		return self._value


class _AStringClass(type(Object)):
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


@addMethodToClass(String, '__call__')
async def String__call(cls, value=''):
	if isinstance(value, type(Object)):
		toStringMethod = await value.getAttribute(String)
		return await toStringMethod.call()

	self = _AString({'__class__': cls})
	self._value = value
	return self


type(Object).String = String
