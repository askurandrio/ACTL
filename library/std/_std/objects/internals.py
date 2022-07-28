from actl.objects import NativeFunction


@NativeFunction
async def addMethod(cls, name, method):
	name = str(name)

	self_ = await cls.getAttribute('__self__')
	self_[name] = method
