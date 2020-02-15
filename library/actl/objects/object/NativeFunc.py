from actl.objects.object.NativeObject import NativeObject


def NativeFunc(name):
	def decorator(func):
		funcName = f'NativeFunc<{name}>'
		nativeFunc = NativeObject({'__name__': funcName}, {'call': func})
		return nativeFunc

	return decorator
