# pylint: disable=protected-access
from actl.objects.Number import Number
from actl.objects.Bool import Bool
from actl.objects.String import String
from actl.objects.AToPy import AToPy
from actl.objects.object import BuildClass
from actl.objects.object import AAttributeNotFound
from actl.objects.object import Object


PyToA = BuildClass('PyToA')


@PyToA.addMethodToClass('__call__')
def _(cls, value):
	if isinstance(value, type(Object)):
		return value

	if isinstance(value, bool):
		return Bool.True_ if value else Bool.False_

	if isinstance(value, (int, float)):
		return Number.call(value)

	self = cls.super_(PyToA, '__call__').call()
	self._value = value
	return self


@PyToA.addMethodToClass('eval')
def _(cls, code):
	code = str(AToPy(code))
	return cls.call(eval(code))  # pylint: disable=eval-used


@PyToA.addMethod('__call__')
def _(self, *args, **kwargs):
	args = [AToPy(arg) for arg in args]
	kwargs = {key: AToPy(value) for key, value in kwargs.items()}
	res = self._value(*args, **kwargs)
	return PyToA.call(res)


@PyToA.addMethod('__getAttribute__')
def _(self, key):
	try:
		return self.super_(PyToA, '__getAttribute__').call(key)
	except AAttributeNotFound:
		pass

	if isinstance(key, str):
		try:
			value = getattr(self._value, key)
		except AttributeError:
			pass
		else:
			return PyToA.call(value)
	raise AAttributeNotFound(key)


@PyToA.addMethod(AToPy)
def _(self):
	return self._value


@PyToA.addMethod(Bool)
def _(self):
	res = bool(self._value)
	return Bool.True_ if res else Bool.False_


@PyToA.addMethod(String)
def _(self):
	return String.call(str(self._value))
