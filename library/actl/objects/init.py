from actl.objects.AToPy import AToPy
from actl.objects.object import Object, NativeObject
from actl.objects.object import BuildClass
from actl.objects.String import String


@String.addMethod(AToPy)
def _(self):
	return self._value  # pylint: disable=protected-access


@BuildClass.addMethodToClass(Object, String)
def _(self):
	name = self.getAttr('__name__')
	return String.call(f"class '{name}'")


@BuildClass.addMethod(Object, String)
def _(self):
	name = self.getAttr('__class__').getAttr('__name__')
	scope = self._head   # pylint: disable=protected-access
	return String.call(f'{name}<{scope}>')


@BuildClass.addMethodToClass(Object, String)
def _(self):
	name = self.getAttr('__name__')
	return String.call(f"class '{name}'")
