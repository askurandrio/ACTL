# pylint: disable=protected-access
from actl.Result import Result
from actl.objects.Bool import Bool
from actl.objects.AToPy import AToPy
from actl.objects.object import makeClass
from actl.objects.object.utils import addMethod, addMethodToClass


Number = makeClass('Number')


@addMethodToClass(Number, '__call__')
def _(cls, value):
	resultSelf = cls.super_.obj(Number, '__call__').obj.call.obj()
	if isinstance(value, str):
		if '.' in value:
			value = float(value)
		else:
			value = int(value)
	resultSelf.obj._value = value
	return resultSelf


@addMethod(Number, Bool)
def _(self):
	if self._value == 0:
		return Result(obj=Bool.False_)
	return Result(obj=Bool.True_)


@addMethod(Number, AToPy)
def _(self):
	return self._value
