from actl.objects.object.NativeClass import NativeClass


class NativeFunc(NativeClass):
	def __init__(self, name, func):
		super().__init__()
		self._name = name
		self._func = func

	def call(self, *args, **kwargs):
		return self._func(*args, **kwargs)

	def __str__(self):
		return f'{type(self).__name__}<{self._name}>'

	@classmethod
	def wrap(cls, name):
		def decorator(func):
			return cls(name, func)
		return decorator
