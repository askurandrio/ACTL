from actl.objects.AToPy import AToPy
from actl.objects.object import Object, AObjectClass
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
	name = self.getAttribute('__class__').getAttribute('__name__')
	head = self._head  # pylint: disable=protected-access
	head = {key: value for key, value in head.items() if key != '__class__'}
	return String.call(f'{name}<{head}>')
