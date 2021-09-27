# pylint: disable=arguments-differ, useless-super-delegation
from actl.objects.object.AObject import AObject
from actl.objects.object.NativeFunction import NativeFunction


class NativeMethod(AObject):
	def __init__(self, rawMethod):
		@NativeFunction
		async def get(aSelf):
			return NativeFunction(self._rawMethod).apply(aSelf)

		super().__init__({})
		self._rawMethod = rawMethod
		self._get = get

	@property
	def class_(self):
		return AObject.Object

	async def lookupSpecialAttribute(self, key):
		if key == '__get__':
			return self, True

		return await super().lookupSpecialAttribute(key)

	async def get(self, instance):
		return await self._get.call(instance)

	async def toPyString(self):
		return f'{type(self).__name__}({self._rawMethod})'
