from actl.objects import NativeFunction, Number


@NativeFunction
async def getStringLength(aString):
	pyString = str(aString)
	pyStringLength = len(pyString)
	return await Number.call(pyStringLength)


@NativeFunction
async def makeString__split(String, Vector):
	@NativeFunction
	async def String__split(self, delimiter):
		pyString = str(self)
		pyDelimiter = str(delimiter)

		vector = await Vector.call()
		vectorAppend = await vector.getAttribute('append')

		for pyStringPart in pyString.split(pyDelimiter):
			await vectorAppend.call(await String.call(pyStringPart))

		return vector

	return String__split
