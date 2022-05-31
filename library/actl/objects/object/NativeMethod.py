# pylint: disable=arguments-differ, useless-super-delegation
from actl.objects.object.AObject import AObject
from actl.objects.object.NativeFunction import NativeFunction
from actl.signals import onSignal


class NativeMethod(AObject):
	def __init__(self, rawMethod):
		@NativeFunction
		async def get(aSelf):
			return await NativeFunction(self._rawMethod).apply(aSelf)

		super().__init__({})

		@onSignal('actl.Object:created', None)
		async def _onObjectCreated(Object):
			self.head['__class__'] = Object

		self._rawMethod = rawMethod
		self._get = get

	async def lookupSpecialAttribute(self, key):
		if key == '__get__':
			return self, True

		return await super().lookupSpecialAttribute(key)

	async def get(self, instance):
		return await self._get.call(instance)

	async def toPyString(self):
		return f'{type(self).__name__}({self._rawMethod})'
