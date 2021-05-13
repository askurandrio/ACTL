from actl.objects.object.AObject import AObject
from actl.objects.object.NativeMethod import NativeMethod
from actl.objects.object.class_ import class_


def makeClass(name, parents=()):
	if makeClass.Object:
		parents = (*parents, makeClass.Object)

	return AObject({
		'__name__': name,
		'__class__': class_,
		'__parents__': parents,
		'__self__': {}
	})


makeClass.Object = None


def addMethod(cls, name):
	def decorator(function):
		aFunction = NativeMethod(function)
		cls.getAttribute('__self__')[name] = aFunction

	return decorator


def addMethodToClass(cls, name):
	def decorator(function):
		aFunction = NativeMethod(function)
		cls.setAttribute(name, aFunction)

	return decorator
