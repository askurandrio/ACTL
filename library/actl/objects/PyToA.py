# pylint: disable=protected-access
from actl.objects.String import String
from actl.objects.AToPy import AToPy
from actl.objects.object import BuildClass, AAttributeNotFound


PyToA = BuildClass('PyToA')


@PyToA.addMethodToClass('__init__')
def _(cls, value):
	self = cls.getAttr('__super__').getAttr('__init__').call()
	self._value = value
	return self


@PyToA.addMethod('__call__')
def _(self, *args):
	args = tuple(AToPy(arg) for arg in args)
	res = self._value(*args)
	return PyToA.call(res)


@PyToA.addMethod('__getAttr__')
def _(self, key):
	try:
		return self.getAttr('__super__').getAttr('__getAttr__').call(key)
	except AAttributeNotFound:
		pass
	try:
		value = getattr(self._value, key)
	except AttributeError as ex:
		raise AAttributeNotFound(ex)
	return PyToA.call(value)


@PyToA.addMethod('__toStr__')
def _(self):
	return String.call(self._value.__name__)


@PyToA.addPyMethod('fromPy')
def _(cls, obj):
	return cls.call(obj)