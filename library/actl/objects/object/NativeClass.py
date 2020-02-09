from actl.objects.object.Object import Object


class NativeClass(type(Object)):
	def __init__(self, initScope=None):
		if initScope is None:
			initScope = {}
		initScope.update({'__class__': self.__aCls})
		super().__init__(initScope)

	def __init_subclass__(cls):
		super().__init_subclass__()
		aCls = type(Object)()
		aCls.setAttr('__class__', Object)
		aCls.setAttr('__parents__', [Object])
		aCls.setAttr('__name__', cls.__name__)
		cls.__aCls = aCls
