from actl.objects.object.NativeClass import NativeClass
from actl.objects.object.NativeFunc import NativeFunc


class NativeProperty(NativeClass):
	def __init__(self, fget):
		super().__init__({'__get__': fget})
		self._fget = fget

	def get(self, instance):
		return self._fget.call(instance)

	def __str__(self):
		return f'{type(self).__name__}({self._fget})'

	@classmethod
	def makeMethod(cls, name, func):
		@NativeFunc.wrap(f'fget_{name}')
		def fget(instance):
			@NativeFunc.wrap(f'fgetWrapper_{name}')
			def wrapper(*args, **kwargs):
				return func(instance, *args, **kwargs)
			return wrapper
		return cls(fget)
