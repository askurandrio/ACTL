from actl.objects import NativeFunction, Number


@NativeFunction
async def getStringLength(aString):
	pyString = await aString.toPyString()
	pyStringLength = len(pyString)
	return await Number.call(pyStringLength)
