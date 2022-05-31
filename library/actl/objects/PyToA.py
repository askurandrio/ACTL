# pylint: disable=protected-access
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
async def _PyToA__call(cls, value):
	if isinstance(value, type(Object)):
		return value

	if isinstance(value, bool):
		return Bool.True_ if value else Bool.False_

	if isinstance(value, (int, float)):
		return Number.call(value)

	superCall = await cls.super_(PyToA, '__call__')
	self = await superCall.call()
	self._value = value
	return self


@addMethodToClass(PyToA, 'eval')
async def _PyToA__eval(cls, code):
	code = str(AToPy(code))
	result = eval(code)  # pylint: disable=eval-used
	return await cls.call(result)


@addMethod(PyToA, '__call__')
async def _PyToA__call(self, *args, **kwargs):
	args = [AToPy(arg) for arg in args]
	kwargs = {key: AToPy(value) for key, value in kwargs.items()}
	res = self._value(*args, **kwargs)
	return await PyToA.call(res)


@addMethod(PyToA, '__getAttribute__')
async def _PyToA__getAttribute(self, key):
	superGetAttribute = await self.super_(PyToA, '__getAttribute__')

	try:
		return await superGetAttribute.call(key)
	except AAttributeNotFound.class_(key=key):
		pass

	if isinstance(key, str):
		try:
			value = getattr(self._value, key)
		except AttributeError:
			pass
		else:
			return await PyToA.call(value)

	raise AAttributeNotFound(key)


@addMethod(PyToA, '__setAttribute__')
async def _PyToA__setAttribute(self, key, value):
	setattr(self._value, key, value)


@addMethod(PyToA, AToPy)
async def _PyToA__AToPY(self):
	return self._value


@addMethod(PyToA, Bool)
async def _PyToA__Bool(self):
	res = bool(self._value)
	return Bool.True_ if res else Bool.False_


@addMethod(PyToA, String)
async def _PyToA__String(self):
	return await String.call(str(self._value))
