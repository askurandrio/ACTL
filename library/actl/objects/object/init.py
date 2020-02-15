from actl.objects.object.BuildClass import BuildClass
from actl.objects.object.NativeDict import NativeDict
from actl.objects.object.NativeProperty import NativeProperty
from actl.objects.object.exceptions import AAttributeIsNotSpecial
from actl.objects.object.utils import loadPropIfNeed
from actl.objects.object.Object import Object


Object.setAttr('__name__', 'Object')


@Object.addPyMethod('fromPy')
def _(_, head):
	return type(Object)(head)


def _Object__getAttr__(self, key):
	try:
		return self._getSpecialAttr(key)  # pylint: disable=protected-access
	except AAttributeIsNotSpecial:
		pass

	attr = self.findAttr(key)
	return loadPropIfNeed(self, attr)


Object.setAttr('__getAttr__', NativeProperty.makeMethod('Object.__getAttr__', _Object__getAttr__))
Object.setAttr('__self__', NativeDict({}))
Object.getAttr('__self__').setItem(
	'__getAttr__', NativeProperty.makeMethod('Object.__self__.__getAttr__', _Object__getAttr__)
)


@BuildClass.addMethodToClass(Object, '__init__')
def _(cls):
	self = type(Object)({})
	self.setAttr('__class__', cls)
	return self


@BuildClass.addMethodToClass(Object, '__call__')
def _(cls, *args, **kwargs):
	return cls.getAttr('__init__').call(*args, **kwargs)
