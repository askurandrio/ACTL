from actl.objects.AToPy import AToPy
from actl.objects.object import Object, class_
from actl.objects.String import String
from actl.objects.object.utils import addMethod


@addMethod(String, AToPy)
async def _String__AToPy(self):
	return self._value  # pylint: disable=protected-access


@addMethod(class_, String)
async def clsAsStr(self):
	name = await self.getAttribute('__name__')
	return await String.call(f"class '{name}'")


@addMethod(Object, String)
async def selfAsStr(self):
	pyString = await self.toPyString()
	return await String.call(pyString)
