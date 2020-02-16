# pylint: disable=protected-access
from actl.objects.BuildClass import BuildClass


class _BuildClassString(BuildClass):
	def __str__(self):
		name = self.getAttr('__name__')
		return f"class '{name}'"


String = _BuildClassString('String')


@String.addMethodToClass('__call__')
def _(cls, value=''):
	s = cls.getAttr('__super__').getAttr('__call__')
	self = s.call()
	self._value = value
	return self


@String.addPyMethod('fromPy')
def _(cls, value):
	return cls.call(value)
