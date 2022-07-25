from actl.objects.AToPy import AToPy
from actl.objects.object import Object, class_
from actl.objects.String import String


@String.addMethod(AToPy)
async def _String__AToPy(self):
	return await self.toPyString()


@class_.addMethod(String)
async def clsAsStr(self):
	name = await self.getAttribute('__name__')
	return await String.call(f"class '{name}'")


@Object.addMethod(String)
async def selfAsStr(self):
	pyString = await self.toPyString()
	return await String.call(pyString)
