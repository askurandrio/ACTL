from actl.objects.object.NativeFunc import NativeFunc
from actl.objects.object.NativeProperty import NativeProperty
from actl.objects.object.exceptions import AAttributeNotFound


def loadPropIfNeed(self, val):
	try:
		prop = val.get
	except (AAttributeNotFound, AttributeError):
		return val
	else:
		return prop(self)


def makeMethod(name, func):
	func = NativeFunc(name, func)
	@NativeFunc.wrap(f'fget_{func}')
	def fget(instance):
		@NativeFunc.wrap(f'fgetWrapper_{func}')
		def wrapper(*args, **kwargs):
			return func.call(instance, *args, **kwargs)
		return wrapper
	return NativeProperty(fget)
