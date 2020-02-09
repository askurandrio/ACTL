from actl.objects.object.NativeClass import NativeClass


class NativeProperty(NativeClass):
	def __init__(self, fget):
		super().__init__()
		self._fget = fget

	def get(self, instance):
		return self._fget.call(instance)

	def __str__(self):
		return f'{type(self).__name__}({self._fget})'
