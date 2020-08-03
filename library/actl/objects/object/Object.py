from actl.objects.object.AObject import AObject
from actl.objects.object.native import nativeMethod, nativeDict
from actl.objects.object.exceptions import AAttributeIsNotSpecial
from actl.objects.object.utils import loadPropIfNeed


def Object__getAttr(self, key):
	try:
		return self.getSpecialAttr(key)
	except AAttributeIsNotSpecial:
		pass

	attr = self.findAttr(key)
	return loadPropIfNeed(self, attr)


def Object__call(cls):
	self = AObject({})
	self.setAttr('__class__', cls)
	return self


Object = AObject({
	'__name__': 'Object',
	'__isClass__': True,
	'__parents__': (),
	'__getAttr__': nativeMethod('Object.__getAttr__', Object__getAttr),
	'__call__': nativeMethod('Object.__call__', Object__call),
	'__self__': nativeDict({
		'__getAttr__': nativeMethod('Object.__getAttr__', Object__getAttr)
	})
})
