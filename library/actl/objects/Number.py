# pylint: disable=protected-access
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
		return Bool.False_
	return Bool.True_


@addMethod(Number, String)
def _Number__String(self):
	class_ = self.getAttribute('__class__')
	className = class_.getAttribute('__name__')
	toStr = f'{className}<{self._value}>'
	return String.call(toStr)


@addMethod(Number, AToPy)
def _Number__AToPy(self):
	return self._value
