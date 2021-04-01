# pylint: disable=protected-access
from actl.objects.Bool import Bool
from actl.objects.AToPy import AToPy
from actl.objects.object import makeClass
from actl.objects.object.utils import addMethod, addMethodToClass


Number = makeClass('Number')


@addMethodToClass(Number, '__call__')
def _(cls, value):
	self = cls.super_(Number, '__call__').call()
	if isinstance(value, str):
		if '.' in value:
			value = float(value)
		else:
			value = int(value)
	self._value = value
	return self


@addMethod(Number, Bool)
def _(self):
	if self._value == 0:
		return Bool.False_
	return Bool.True_


@addMethod(Number, AToPy)
def _(self):
	return self._value
