# pylint: disable=protected-access
from actl.objects.object.Object import Object
from actl.objects.object.NativeMethod import NativeMethod
from actl.objects.object.AObjectClass import AObjectClass


class BuildClass(AObjectClass):
	def __init__(self, name):
		super().__init__({
			'__name__': name,
			'__parents__': (Object,),
			'__self__': {}
		})

	def addMethod(self, name):
		def decorator(function):
			aFunction = NativeMethod(function)
			self.getAttribute('__self__')[name] = aFunction

		return decorator

	def addMethodToClass(self, name):
		def decorator(function):
			aFunction = NativeMethod(function)
			self.setAttribute(name, aFunction)

		return decorator
