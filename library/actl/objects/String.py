# pylint: disable=protected-access
from actl.objects.object import BuildClass


class _BuildClassString(BuildClass):
	def __str__(self):
		name = self.getAttr('__name__')
		return f"class '{name}'"


String = _BuildClassString('String')


@String.addMethodToClass('__init__')
def _(cls, value=''):
	self = cls.getAttr('__super__').getAttr('__init__').call()
	self._value = value
	return self


@String.addPyMethod('fromPy')
def _(cls, value):
	return cls.call(value)
