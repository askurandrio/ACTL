# pylint: disable=arguments-differ, useless-super-delegation
from actl.objects.object.AObject import AObject


class NativeObject(AObject):
	def lookupSpecialAttribute(self, key):
		from actl.objects.object.Object import Object

		if key != '__class__':
			return super().lookupSpecialAttribute(key)

		return Object


class NativeMethod(NativeObject):
	def __init__(self, rawMethod):
		@NativeFunction
		def get(aSelf):
			@NativeFunction
			def method(*args, **kwargs):
				return rawMethod(aSelf, *args, **kwargs)

			return method

		super().__init__({})
		self._get = get

	def lookupSpecialAttribute(self, key):
		if key != '__get__':
			return super().lookupSpecialAttribute(key)

		return self._get


class NativeFunction(NativeObject):
	def __init__(self, function):
		self._function = function
		super().__init__({})

	def call(self, *args, **kwargs):
		return self._function(*args, **kwargs)
