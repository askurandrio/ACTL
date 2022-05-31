from actl.objects.object.AObject import AObject
from actl.objects.object._AppliedFunction import AppliedFunction
from actl.signals import onSignal


class NativeFunction(AObject):
	def __init__(self, function):
		self._function = function
		super().__init__({})

		@onSignal('actl.Object:created', None)
		async def _onObjectCreated(Object):
			self._head['__class__'] = Object

	async def call(self, *args, **kwargs):
		return await self._function(*args, **kwargs)

	async def toPyString(self):
		return f'{type(self).__name__}({self._function})'

	def apply(self, *args):
		return type(self)(AppliedFunction(self._function, *args))

	async def lookupSpecialAttribute(self, key):
		if key == '__call__':
			return self, True

		return await super().lookupSpecialAttribute(key)

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False
		return self._function == other._function
