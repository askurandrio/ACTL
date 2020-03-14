# pylint: disable=protected-access
from actl.objects.BuildClass import BuildClass


class _BuildClassString(BuildClass):
	def __str__(self):
		name = self.getAttr('__name__')
		return f"class '{name}'"


String = _BuildClassString('String')


@String.addMethodToClass('__call__')
def _(cls, value=''):
	self = cls.super_(String, '__call__').call()
	self._value = value
	return self


@String.addPyMethod('fromPy')
def _(cls, value):
	return cls.call(value)
