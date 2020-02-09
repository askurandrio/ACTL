# pylint: disable=protected-access

from actl.objects.String import String
from actl.objects.Object import BuildClass, ANotFoundAttribute


PyToA = BuildClass('PyToA')


@PyToA.addMethodToClass('__init__')
def _(cls, value):
	self = cls.getAttr('__super__').getAttr('__init__').call()
	self._value = value
	return self


@PyToA.addMethod('__call__')
def _(self, *args):
	def toPyValue(arg):
		if arg.getAttr('__class__').equal(PyToA) or arg.getAttr('__class__').equal(String):
			return arg._value
		return str(arg)

	args = tuple(toPyValue(arg) for arg in args)
	self._value(*args)


@PyToA.addMethod('__getAttr__')
def _(self, key):
	try:
		return self.getAttr('__super__').getAttr('__getAttr__').call(key)
	except ANotFoundAttribute:
		pass
	try:
		value = getattr(self._value, key)
	except AttributeError as ex:
		raise ANotFoundAttribute(ex)
	return PyToA.call(value)


@PyToA.addMethod('__toStr__')
def _(self):
	return self._value.__name__


@PyToA.addPyMethod('fromPy')
def _(cls, obj):
	return cls.call(obj)
