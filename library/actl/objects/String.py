# pylint: disable=protected-access
from actl.objects.AToPy import AToPy
from actl.objects.object import BuildClass


String = BuildClass('String')


@String.addMethodToClass('__init__')
def _(cls, value=''):
	self = cls.getAttr('__super__').getAttr('__init__').call()
	self._value = value
	return self


@String.addMethod(AToPy)
def _(self):
	return AToPy(self._value)


@String.addPyMethod('fromPy')
def _(cls, value):
	return cls.call(value)
