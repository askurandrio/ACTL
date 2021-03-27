from actl.objects.object import Object, nativeMethod, nativeDict


class BuildClass(type(Object)):
	def __init__(self, name, *parents):
		super().__init__({
			'__name__': name,
			'__class__': Object,
			'__parents__': parents + (Object,),
			'__isClass__': True,
			'__self__': nativeDict({})
		})

	def addMethod(self, attr):
		def decorator(func):
			clsName = self.getAttr('__name__')
			clsName = clsName[0].lower() + clsName[1:]
			methodName = f'{clsName}.{attr}'
			method = nativeMethod(methodName, func)
			self.getAttr('__self__').setItem(attr, method)
			return func

		return decorator

	def addMethodToClass(self, attr):
		def decorator(func):
			clsName = self.getAttr('__name__')
			methodName = f'{clsName}.{attr}'
			method = nativeMethod(methodName, func)
			self.setAttr(attr, method)
			return func

		return decorator
