from actl.objects.AToPy import AToPy
from actl.objects.object import Object, makeClass
from actl.objects.String import String
from actl.objects.object.utils import addMethod, addMethodToClass


@addMethod(String, AToPy)
def _(self):
	return self._value  # pylint: disable=protected-access


@addMethodToClass(Object, String)
def clsAsStr(self):
	name = self.getAttribute('__name__')
	return String.call(f"class '{name}'")


@addMethod(Object, String)
def selfAsStr(self):
	pySting = self.toPyString()
	return String.call(pySting)
