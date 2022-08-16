# pylint: disable=protected-access
from actl.objects.Bool import Bool
from actl.objects.String import String
from actl.objects.AToPy import AToPy
from actl.objects.object import class_, AObject

from actl.utils import executeSyncCoroutine
from actl.signals import triggerSignal


Number = executeSyncCoroutine(class_.call('Number'))


@Number.addMethod('__init__')
async def _Number__init(self, value):
	if isinstance(value, str):
		if '.' in value:
			value = float(value)
		else:
			value = int(value)

	elif isinstance(value, AObject):
		toNumberMethod = await value.getAttribute(Number)
		value = await toNumberMethod.call()
		value = value._value
	elif not isinstance(value, (int, float)):
		raise RuntimeError(f'Invalid number: {value}')

	self._value = value


@Number.addMethod(Bool)
async def _Number__Bool(self):
	if self._value == 0:
		return Bool.False_
	return Bool.True_


@Number.addMethod(String)
async def _Number__String(self):
	cls = await self.getAttribute('__class__')
	className = await cls.getAttribute('__name__')
	toStr = f'{className}<{self._value}>'
	return await String.call(toStr)


@Number.addMethod(AToPy)
async def _Number__AToPy(self):
	return self._value


executeSyncCoroutine(triggerSignal('actl.Number:created', Number))
