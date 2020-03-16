from actl.objects.object import Object, ClassObject, nativeMethod, nativeDict


class BuildClass(ClassObject):
	def __init__(self, name, *parents):
		super().__init__({})
		self.setAttr('__name__', name)
		self.setAttr('__parents__', parents + (Object,))
		self.setAttr('__self__', nativeDict({}))

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
