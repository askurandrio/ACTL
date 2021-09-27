from actl.objects import NativeFunction


@NativeFunction
async def getStringLength(aString):
	pyString = await aString.toPyString()
	return len(pyString)
