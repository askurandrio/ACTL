from actl.objects.SuperSelf import SuperSelf
from actl.objects.object import Object, nativeMethod
from actl.objects.Super import Super


class BuildClass(type(Object)):
	def __init__(self, name, parents=None):
		cls = Object.getAttr('__class__').call(name)
		super().__init__(cls._head)
		if parents is None:
			parents = []
		parents.append(Object)
		self.setAttr('__parents__', parents)
		self.setAttr('__super__', Super(parents))  # pylint: disable=no-value-for-parameter
		self.getAttr('__self__').setItem('__super__', SuperSelf(parents))  # pylint: disable=no-value-for-parameter

	def addMethod(self, attr):
		def decorator(func):
			cls_name = self.getAttr('__name__')
			cls_name = cls_name[0].lower() + cls_name[1:]
			methodName = f'{cls_name}.{attr}'
			method = nativeMethod(methodName, func)
			self.getAttr('__self__').setItem(attr, method)
			return func

		return decorator

	def addMethodToClass(self, attr):
		def decorator(func):
			cls_name = self.getAttr('__name__')
			methodName = f'{cls_name}.{attr}'
			method = nativeMethod(methodName, func)
			self.setAttr(attr, method)
			return func

		return decorator
