from actl.objects.object.NativeDict import NativeDict
from actl.objects.object.Object import Object
from actl.objects.object.Super import Super
from actl.objects.object.SuperSelf import SuperSelf
from actl.objects.object.utils import makeMethod


class BuildClass(type(Object)):
	def __init__(self, name, parents=None):
		super().__init__()
		if parents is None:
			parents = []
		parents.append(Object)
		self.setAttr('__class__', Object)
		self.setAttr('__parents__', parents)
		self.setAttr('__name__', name)
		self.setAttr('__super__', Super.make(parents))
		self.setAttr('__self__', NativeDict({'__super__': SuperSelf.make(parents)}))

	def addMethod(self, name):
		def decorator(func):
			cls_name = self.getAttr('__name__')
			cls_name = cls_name[0].lower() + cls_name[1:]
			func.__name__ = f'{cls_name}.{name}'
			method = makeMethod(func.__name__, func)
			self.getAttr('__self__').setItem(name, method)
			return func

		return decorator

	def addMethodToClass(self, name):
		def decorator(func):
			cls_name = self.getAttr('__name__')
			func.__name__ = f'{cls_name}.{name}'
			method = makeMethod(func.__name__, func)
			self.setAttr(name, method)
			return func

		return decorator
