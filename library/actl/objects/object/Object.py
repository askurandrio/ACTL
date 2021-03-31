from actl.objects.object.AObject import AObject
from actl.objects.object.utils import addMethod, addMethodToClass, makeClass


def Object__getAttribute(self, key):
	return self.lookupAttribute(key)


def Object__call(self, *args, **kwargs):
	instance = AObject({'__class__': self})
	instance.getAttribute('__init__').call(*args, **kwargs)
	return instance


def object__init(self):
	pass


def object__getAttribute(self, key):
	return self.lookupAttribute(key)


Object = makeClass('Object')
Object.setAttribute('__name__', 'Object')
addMethodToClass(Object, '__call__')(Object__call)
addMethod(Object, '__getAttribute__')(Object__getAttribute)
