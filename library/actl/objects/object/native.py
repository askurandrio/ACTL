# pylint: disable=arguments-differ, invalid-overridden-method, useless-super-delegation

from actl.objects.object.exceptions import AKeyNotFound, AAttributeNotFound
from actl.objects.object.InstanceObject import InstanceObject


class _NativeObject(InstanceObject):
	def __init__(self, aAttributes, pyAttibutes):
		for key, value in pyAttibutes.items():
			setattr(self, key, value)
		super().__init__(aAttributes)

	def asStr(self):
		return f'{type(self).__name__}<...>'

	def call(self, *args, **kwargs):
		return super().call(*args, **kwargs)

	def get(self, instance):
		return super().get(instance)

	def getAttr(self, key):
		try:
			return self._head[key]
		except KeyError:
			pass

		from actl.objects.String import String  # pylint: disable=cyclic-import, import-outside-toplevel

		if key == String:
			@nativeFunc('NativeObject.asStr')
			def asStr():
				return String.fromPy(self.asStr())

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
		attr = f'{name}.__get__()'
		try:
			return getattr(instance, attr)
		except AttributeError:
			pass

		@nativeFunc(attr)
		def wrapper(*args, **kwargs):
			return func(instance, *args, **kwargs)

		setattr(instance, attr, wrapper)
		return fget.call(instance)

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
