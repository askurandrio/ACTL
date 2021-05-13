# pylint: disable=protected-access
from actl.objects.object import Object, class_, Result
from actl.objects.object.utils import addMethod, addMethodToClass


class _AString(type(Object)):
	def toPyString(self):
		return self._value


class _AStringClass(type(Object)):
	def __str__(self):
		return "class 'String'"


String = _AStringClass({
	'__name__': 'String',
	'__class__': class_,
	'__parents__': (Object,),
	'__self__': {}
})


@addMethodToClass(String, '__call__')
def String__call(cls, value=''):
	if isinstance(value, type(Object)):
		return value.getAttribute(String).call()

	self = _AString({'__class__': cls})
	self._value = value
	return self
