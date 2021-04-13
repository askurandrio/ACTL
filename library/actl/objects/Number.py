# pylint: disable=protected-access
from actl.Result import Result
from actl.objects.Bool import Bool
from actl.objects.String import String
from actl.objects.AToPy import AToPy
from actl.objects.object import makeClass
from actl.objects.object.utils import addMethod


Number = makeClass('Number')


@addMethod(Number, '__init__')
def _Number__init(self, value):
	if isinstance(value, str):
		if '.' in value:
			value = float(value)
		else:
			value = int(value)
	self._value = value


@addMethod(Number, Bool)
def _Number__Bool(self):
	if self._value == 0:
		return Result.fromObj(Bool.False_)
	return Result.fromObj(Bool.True_)


@addMethod(Number, String)
def _Number__String(self):
	class_ = self.getAttribute.obj('__class__').obj
	className = class_.getAttribute.obj('__name__').obj
	toStr = f'{className}<{self._value}>'
	return String.call.obj(toStr)


@addMethod(Number, AToPy)
def _(self):
	return self._value
