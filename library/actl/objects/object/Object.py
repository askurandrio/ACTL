from actl.objects.object.native import nativeMethod, nativeDict
from actl.objects.object.exceptions import AAttributeIsNotSpecial
from actl.objects.object.utils import loadPropIfNeed
from actl.objects.object._Object import Object as pyObjectCls


def getAttr(self, key):
	try:
		return self._getSpecialAttr(key)  # pylint: disable=protected-access
	except AAttributeIsNotSpecial:
		pass

	attr = self.findAttr(key)
	return loadPropIfNeed(self, attr)


def selfCall(cls):
	self = pyObjectCls({})
	self.setAttr('__class__', cls)
	return self


def clsCall(cls, name):
	self = pyObjectCls({})
	self.setAttr('__name__', name)
	self.setAttr('__class__', cls)
	self.setAttr('__self__', nativeDict({}))
	return self


_Object = pyObjectCls({
	'__name__': '_Object',
	'__call__': nativeMethod('_Object.__call__', clsCall),
	'__getAttr__': nativeMethod('_Object.__getAttr__', getAttr),
	'__self__': nativeDict({
		'__call__': nativeMethod('Object.__call__', selfCall),
		'__getAttr__': nativeMethod('Object.__getAttr__', getAttr),
	})
})


Object = _Object.call('Object')
Object.getAttr('__self__').setItem('__getAttr__', nativeMethod('object.__getAttr__', getAttr))


@Object.addPyMethod('fromPy')
def _(_, head):
	return type(Object)(head)
