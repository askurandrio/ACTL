from actl.objects.AToPy import AToPy
from actl.objects.object import Object, class_
from actl.objects.String import String
from actl.objects.object.utils import addMethod


@addMethod(String, AToPy)
def _String__AToPy(self):
	return self._value  # pylint: disable=protected-access


@addMethod(class_, String)
def clsAsStr(self):
	name = self.getAttribute('__name__')
	return String.call(f"class '{name}'")


@addMethod(Object, String)
def selfAsStr(self):
	pySting = self.toPyString()
	return String.call(pySting)
