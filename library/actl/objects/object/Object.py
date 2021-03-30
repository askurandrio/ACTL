from actl.objects.object.NativeMethod import NativeMethod
from actl.objects.object.AObject import AObject
from actl.objects.object.AObjectClass import AObjectClass


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


Object = AObjectClass({
	'__name__': 'Object',
	'__parents__': (),
	'__getAttribute__': NativeMethod(Object__getAttribute),
	'__call__': NativeMethod(Object__call),
	'__self__': {
		'__init__': NativeMethod(object__init),
		'__getAttribute__': NativeMethod(object__getAttribute)
	}
})
