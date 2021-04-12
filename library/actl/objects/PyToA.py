# pylint: disable=protected-access
from actl.Result import Result
from actl.objects.Number import Number
from actl.objects.Bool import Bool
from actl.objects.String import String
from actl.objects.AToPy import AToPy
from actl.objects.object import makeClass
from actl.objects.object import AAttributeNotFound
from actl.objects.object import Object
from actl.objects.object.utils import addMethod, addMethodToClass


PyToA = makeClass('PyToA')


@addMethodToClass(PyToA, '__call__')
def _(cls, value):
	if isinstance(value, type(Object)):
		return Result(obj=value)

	if isinstance(value, bool):
		return Result(obj=Bool.True_) if value else Result(obj=Bool.False_)

	if isinstance(value, (int, float)):
		return Number.call(value)

	resultSelf = cls.super_.obj(PyToA, '__call__').obj.call.obj()
	resultSelf.obj._value = value
	return resultSelf


@addMethodToClass(PyToA, 'eval')
def _(cls, code):
	code = str(AToPy(code))
	return cls.call(eval(code))  # pylint: disable=eval-used


@addMethod(PyToA, '__call__')
def _(self, *args, **kwargs):
	args = [AToPy(arg) for arg in args]
	kwargs = {key: AToPy(value) for key, value in kwargs.items()}
	res = self._value(*args, **kwargs)
	return PyToA.call.obj(res)


@addMethod(PyToA, '__getAttribute__')
def _(self, key):
	try:
		return self.super_.obj(PyToA, '__getAttribute__').obj.call.obj(key)
	except AAttributeNotFound:
		pass

	if isinstance(key, str):
		try:
			value = getattr(self._value, key)
		except AttributeError:
			pass
		else:
			return PyToA.call.obj(value)
	raise AAttributeNotFound(key)


@addMethod(PyToA, AToPy)
def _(self):
	return self._value


@addMethod(PyToA, Bool)
def _(self):
	res = bool(self._value)
	return Result(obj=Bool.True_) if res else Result(obj=Bool.False_)


@addMethod(PyToA, String)
def _(self):
	return String.call.obj(str(self._value))
