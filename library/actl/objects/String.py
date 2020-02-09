# pylint: disable=protected-access

from actl.objects.Object import BuildClass


String = BuildClass('String')


@String.addMethodToClass('__init__')
def _(cls, value=''):
	self = cls.getAttr('__super__').getAttr('__init__').call()
	self._value = value
	return self


@String.addPyMethod('fromPy')
def _(cls, value):
	return cls.call(value)
