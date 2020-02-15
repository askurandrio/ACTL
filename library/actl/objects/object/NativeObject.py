from actl.objects.object.Object import Object


class NativeObject(type(Object)):
	_aCls = type(Object)({})
	_aCls.setAttr('__class__', Object)
	_aCls.setAttr('__parents__', [Object])
	_aCls.setAttr('__name__', 'NativeObject')

	def __init__(self, aAttributes, pyAttibutes):
		aAttributes['__class__'] = self._aCls
		for key, value in pyAttibutes.items():
			setattr(self, key, value)
		super().__init__(aAttributes)
