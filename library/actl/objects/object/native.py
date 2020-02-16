from actl.objects.object.exceptions import AKeyNotFound, AAttributeNotFound
from actl.objects.object._Object import Object as pyObjectCls\


class _NativeObject(pyObjectCls):
	aCls = pyObjectCls({})
	aCls.setAttr('__name__', 'NativeObject')

	def __init__(self, aAttributes, pyAttibutes):
		aAttributes['__class__'] = self.aCls
		for key, value in pyAttibutes.items():
			setattr(self, key, value)
		super().__init__(aAttributes)

	def getAttr(self, key):
		from actl.objects.String import String

		try:
			return self._head[key]
		except KeyError:
			pass

		if key == String:
			@nativeFunc('NativeObject.asStr')
			def asStr():
				return String.fromPy(str(self))

			return asStr

		raise AAttributeNotFound(key)

	def __str__(self):
		return self.asStr()


def nativeFunc(name):
	def decorator(func):
		def asStr():
			return f'nativeFunc<{name}>'

		return _NativeObject({}, {'call': func, 'asStr': asStr})

	return decorator


def nativeProperty(fget):
	def get(instance):
		return fget.call(instance)

	def asStr():
		return f'nativeProperty({fget})'

	return _NativeObject({}, {'get': get, 'asStr': asStr})


def nativeMethod(name, func):
	@nativeFunc(f'{name}.__get__')
	def fget(instance):
		@nativeFunc(f'{name}.__get__()')
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

	return _NativeObject({}, {'asStr': asStr, 'setItem': setItem, 'getItem': getItem})
