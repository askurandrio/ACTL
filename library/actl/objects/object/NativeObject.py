from actl.objects.object.Object import Object


class NativeObject(type(Object)):
	aCls = type(Object)({})
	aCls.setAttr('__class__', Object)
	aCls.setAttr('__parents__', [Object])
	aCls.setAttr('__name__', 'NativeObject')

	def __init__(self, aAttributes, pyAttibutes):
		aAttributes['__class__'] = self.aCls
		for key, value in pyAttibutes.items():
			setattr(self, key, value)
		super().__init__(aAttributes)

	@classmethod
	def nativeFunc(cls, name):
		def decorator(func):
			asStr = lambda: f'NativeFunc<{name}>'
			nativeFunc = cls({}, {'call': func, 'asStr': asStr})
			return nativeFunc

		return decorator

	@classmethod
	def nativeProperty(cls, fget):
		get = lambda instance: fget.call(instance)
		asStr = lambda: f'NativeProperty({fget})'
		nativeProperty = cls({}, {'get': get, 'asStr': asStr})
		return nativeProperty

	@classmethod
	def nativeMethod(cls, name, func):
		@cls.nativeFunc(f'fget_{name}')
		def fget(instance):
			@cls.nativeFunc(f'fgetWrapper_{name}')
			def wrapper(*args, **kwargs):
				return func(instance, *args, **kwargs)
			return wrapper
		return cls.nativeProperty(fget)
