from actl.objects.object.AObject import AObject
from actl.objects.object.NativeMethod import NativeMethod
from actl.objects.object.class_ import class_
from actl.utils import executeSyncCoroutine


def makeClass(name, parents=(), self_=None, extraAttributes=None):
	if AObject.Object:
		parents = [*parents, AObject.Object]

	while (len(parents) > 1) and (parents[-1] == parents[-2]):
		parents.pop(-1)

	self_ = {} if self_ is None else self_
	extraAttributes = {} if extraAttributes is None else extraAttributes

	return AObject(
		{
			'__name__': name,
			'__class__': class_,
			'__parents__': parents,
			'__self__': self_,
			**extraAttributes,
		}
	)


def addMethod(cls, name):
	def decorator(function):
		aFunction = NativeMethod(function)
		self_ = executeSyncCoroutine(cls.getAttribute('__self__'))
		self_[name] = aFunction
		return function

	return decorator


def addMethodToClass(cls, name):
	def decorator(function):
		aFunction = NativeMethod(function)
		cls.setAttribute(name, aFunction)

	return decorator
