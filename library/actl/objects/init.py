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
	name = self.getAttr('__class__').getAttr('__name__')
	scope = self._head   # pylint: disable=protected-access
	return String.call(f'{name}<{scope}>')


Object.getAttr('__class__').setAttr(
	String, nativeMethod('_Object.__str__', clsAsStr)
)
Object.getAttr('__class__').getAttr('__self__').setItem(
	String, nativeMethod('_Object.__str__', clsAsStr)
)
Object.getAttr('__self__').setItem(
	String, nativeMethod('object.__str__', selfAsStr)
)
