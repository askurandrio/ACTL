from actl.objects.AToPy import AToPy
from actl.objects.object import Object, class_
from actl.objects.String import String
from actl.objects.object.utils import addMethod, addMethodToClass


@addMethod(String, AToPy)
def _(self):
	return self._value  # pylint: disable=protected-access


@addMethod(class_, String)
def clsAsStr(self):
	name = self.getAttribute.obj('__name__').obj
	return String.call.obj(f"class '{name}'")


@addMethod(Object, String)
def selfAsStr(self):
	pySting = self.toPyString()
	return String.call.obj(pySting)
