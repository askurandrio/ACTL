from actl.objects.AToPy import AToPy
from actl.objects.object import Object, nativeMethod
from actl.objects.String import String


@String.addMethod(AToPy)
def _(self):
	return self._value  # pylint: disable=protected-access


def clsAsStr(self):
	name = self.getAttr('__name__')
	return String.call(f"class '{name}'")


def selfAsStr(self):
	name = self.class_.getAttr('__name__')
	head = self._head  # pylint: disable=protected-access
	head = {key: value for key, value in head.items() if key != '__class__'}
	return String.call(f'{name}<{head}>')


Object.setAttr(
	String, nativeMethod('Object.__str__', clsAsStr)
)
Object.getAttr('__self__').setItem(
	String, nativeMethod('object.__str__', selfAsStr)
)
