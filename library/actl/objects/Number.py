# pylint: disable=protected-access
from actl.objects.Bool import Bool
from actl.objects.String import String
from actl.objects.AToPy import AToPy
from actl.objects.object import class_

from actl.utils import executeSyncCoroutine


Number = executeSyncCoroutine(class_.call('Number'))


@Number.addMethod('__init__')
async def _Number__init(self, value):
	if isinstance(value, str):
		if '.' in value:
			value = float(value)
		else:
			value = int(value)
	self._value = value


@Number.addMethod(Bool)
async def _Number__Bool(self):
	if self._value == 0:
		return Bool.False_
	return Bool.True_


@Number.addMethod(String)
async def _Number__String(self):
	class_ = await self.getAttribute('__class__')
	className = await class_.getAttribute('__name__')
	toStr = f'{className}<{self._value}>'
	return await String.call(toStr)


@Number.addMethod(AToPy)
async def _Number__AToPy(self):
	return self._value
