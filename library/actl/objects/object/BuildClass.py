from actl.objects.object.native import nativeDict, nativeMethod
from actl.objects.object.Object import Object
from actl.objects.object.Super import Super
from actl.objects.object.SuperSelf import SuperSelf


class BuildClass(type(Object)):
	def __init__(self, name, parents=None):
		super().__init__({})
		if parents is None:
			parents = []
		parents.append(Object)
		self.setAttr('__class__', Object)
		self.setAttr('__parents__', parents)
		self.setAttr('__name__', name)
		self.setAttr('__super__', Super(parents))  # pylint: disable=no-value-for-parameter
		self.setAttr(
			'__self__',
			nativeDict({'__super__': SuperSelf(parents)})  # pylint: disable=no-value-for-parameter
		)

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
