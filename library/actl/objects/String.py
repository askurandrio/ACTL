# pylint: disable=protected-access
from actl.objects.object import Object, class_
from actl.objects.object.utils import addMethodToClass


class _AString(type(Object)):
	def __str__(self):
		name = self.getAttribute('__name__')
		return f"class '{name}'"


String = _AString({
	'__name__': 'String',
	'__self__': {},
	'__class__': class_,
	'__parents__': (Object,),
})


@addMethodToClass(String, '__call__')
def _(cls, value=''):
	self = cls.super_(String, '__call__').call()
	self._value = value
	return self
