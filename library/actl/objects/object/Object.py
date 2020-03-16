from actl.objects.object.InstanceObject import InstanceObject
from actl.objects.object.native import nativeMethod, nativeDict
from actl.objects.object.exceptions import AAttributeIsNotSpecial
from actl.objects.object.utils import loadPropIfNeed
from actl.objects.object.ClassObject import ClassObject


def getAttr(self, key):
	try:
		return self.getSpecialAttr(key)  # pylint: disable=protected-access
	except AAttributeIsNotSpecial as ex:
		ex.check(key)

	attr = self.findAttr(key)
	return loadPropIfNeed(self, attr)


def selfCall(cls):
	self = InstanceObject({})
	self.setAttr('__class__', cls)
	return self


Object = ClassObject({
	'__name__': 'Object',
	'__call__': nativeMethod('Object.__call__', selfCall),
	'__getAttr__': nativeMethod('Object.__getAttr__', getAttr),
	'__parents__': (),
	'__self__': nativeDict({
		'__getAttr__': nativeMethod('object.__getAttr__', getAttr)
	})
})
