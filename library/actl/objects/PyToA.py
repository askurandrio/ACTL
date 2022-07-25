# pylint: disable=protected-access
from actl.objects.Number import Number
from actl.objects.Bool import Bool
from actl.objects.String import String
from actl.objects.AToPy import AToPy
from actl.objects.object import class_, AAttributeNotFound, Object, AObject
from actl.utils import executeSyncCoroutine


PyToA = executeSyncCoroutine(class_.call('PyToA'))


@PyToA.addMethodToClass('__call__')
async def _PyToA__call(cls, value):
	if isinstance(value, AObject):
		return value

	if isinstance(value, bool):
		return Bool.True_ if value else Bool.False_

	if isinstance(value, (int, float)):
		return Number.call(value)

	superCall = await cls.super_(PyToA, '__call__')
	self = await superCall.call()
	self._value = value
	return self


@PyToA.addMethodToClass('exec')
async def _PyToA__exec(cls, code, resultName):
	code = str(AToPy(code))
	lc_scope = {}
	exec(code, None, lc_scope)  # pylint: disable=exec-used
	result = lc_scope[str(resultName)]
	return await cls.call(result)


@PyToA.addMethod('__call__')
async def _PyToA__call(self, *args, **kwargs):
	args = [AToPy(arg) for arg in args]
	kwargs = {key: AToPy(value) for key, value in kwargs.items()}
	res = self._value(*args, **kwargs)
	return await PyToA.call(res)


@PyToA.addMethod('__getAttribute__')
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


@PyToA.addMethod('__setAttribute__')
async def _PyToA__setAttribute(self, key, value):
	setattr(self._value, key, value)


@PyToA.addMethod(AToPy)
async def _PyToA__AToPY(self):
	return self._value


@PyToA.addMethod(Bool)
async def _PyToA__Bool(self):
	res = bool(self._value)
	return Bool.True_ if res else Bool.False_


@PyToA.addMethod(String)
async def _PyToA__String(self):
	return await String.call(str(self._value))
