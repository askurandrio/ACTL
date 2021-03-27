# pylint: disable=protected-access
from actl.objects.Bool import Bool
from actl.objects.AToPy import AToPy
from actl.objects.BuildClass import BuildClass


Number = BuildClass('Number')


@Number.addMethodToClass('__call__')
def _(cls, value):
	self = cls.super_(Number, '__call__').call()
	if isinstance(value, str):
		if '.' in value:
			value = float(value)
		else:
			value = int(value)
	self._value = value
	return self


@Number.addMethod(Bool)
def _(self):
	if self._value == 0:
		return Bool.False_
	return Bool.True_


@Number.addMethod(AToPy)
def _(self):
	return self._value
