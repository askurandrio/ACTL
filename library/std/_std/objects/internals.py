from actl.objects import NativeFunction


@NativeFunction
async def addMethod(cls, name, method):
	name = await name.toPyString()

	cls.self_[name] = method
