# from actl.objects.Number import Number
from actl.objects.Bool import Bool
from actl.objects.String import String
from actl.objects.AToPy import AToPy
from actl.objects.object import class_, AAttributeNotFound, AObject
from actl.utils import executeSyncCoroutine


PyToA = executeSyncCoroutine(class_.call('PyToA'))


@PyToA.addMethodToClass('__call__')
async def _PyToA__call(cls, value):
	superCall = await cls.super_(PyToA, '__call__')
	self = await superCall.call()
	self._value = value
	return self


@PyToA.addMethod('cast')
async def _PyToA__cast(self):
	if isinstance(self._value, AObject):
		return self._value

	if isinstance(self._value, bool):
		return Bool.True_ if self._value else Bool.False_

	if isinstance(self._value, (int, float)):
		return await Number.call(self._value)

	if isinstance(self._value, str):
		return await String.call(self._value)

	return self


@PyToA.addMethod('await')
async def _PyToA__await(self):
	value = await self._value
	return value


@PyToA.addMethodToClass('exec')
async def _PyToA__exec(cls, code, resultName, **lc_scope):
	code = str(AToPy(code))
	exec(code, None, lc_scope)
	result = lc_scope[str(resultName)]
	return await cls.call(result)


@PyToA.addMethod('__call__')
async def _PyToA__call(self, *args, **kwargs):
	noWrap = kwargs.pop('_noWrap', False)

	if not noWrap:
		args = [AToPy(arg) for arg in args]
		kwargs = {key: AToPy(value) for key, value in kwargs.items()}

	res = self._value(*args, **kwargs)

	return await PyToA.call(res)


@PyToA.addMethod('getAttribute')
async def _PyToA__getAttribute(self, key):
	pyKey = AToPy(key)

	try:
		value = getattr(self._value, pyKey)
	except AttributeError as ex:
		raise AAttributeNotFound(pyKey) from ex

	return await PyToA.call(value)


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
	return await String.call(f'PyToA<{self._value}>')
