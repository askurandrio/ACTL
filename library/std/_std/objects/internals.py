from actl.objects import NativeFunction


@NativeFunction
async def addMethod(cls, name, method):
	name = str(name)

	cls.self_[name] = method
