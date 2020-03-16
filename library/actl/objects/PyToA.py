# pylint: disable=protected-access
from actl.objects.Number import Number
from actl.objects.Bool import Bool, ATrue, AFalse
from actl.objects.String import String
from actl.objects.AToPy import AToPy
from actl.objects.BuildClass import BuildClass
from actl.objects.object import AAttributeNotFound


PyToA = BuildClass('PyToA')


@PyToA.addMethodToClass('__call__')
def _(cls, value):
	if isinstance(value, bool):
		return ATrue if value else AFalse

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
def _(self, *args):
	args = tuple(AToPy(arg) for arg in args)
	res = self._value(*args)
	return PyToA.call(res)


@PyToA.addMethod('__getAttr__')
def _(self, key):
	try:
		return self.super_(PyToA, '__getAttr__').call(key)
	except AAttributeNotFound as ex:
		ex.check(key)

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
	return ATrue if res else AFalse


@PyToA.addMethod(String)
def _(self):
	return String.call(str(self._value))
