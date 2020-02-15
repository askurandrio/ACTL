from actl.objects.object.exceptions import AKeyNotFound
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


def nativeFunc(name):
	def decorator(func):
		def asStr():
			return f'nativeFunc<{name}>'

		return NativeObject({}, {'call': func, 'asStr': asStr})

	return decorator


def nativeProperty(fget):
	def get(instance):
		return fget.call(instance)

	def asStr():
		return f'nativeProperty({fget})'

	return NativeObject({}, {'get': get, 'asStr': asStr})


def nativeMethod(name, func):
	@nativeFunc(f'fget_{name}')
	def fget(instance):
		@nativeFunc(f'fgetWrapper_{name}')
		def wrapper(*args, **kwargs):
			return func(instance, *args, **kwargs)
		return wrapper
	return nativeProperty(fget)


def nativeDict(head):
	def asStr():
		return f'nativeDict({head})'

	def setItem(key, value):
		head[key] = value

	def getItem(key):
		try:
			return head[key]
		except KeyError:
			raise AKeyNotFound(key=key)

	return NativeObject({}, {'asStr': asStr, 'setItem': setItem, 'getItem': getItem})
