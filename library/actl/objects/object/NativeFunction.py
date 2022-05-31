from actl.objects.object.AObject import AObject
from actl.objects.object._AppliedFunction import AppliedFunction
from actl.objects.object.exceptions import AAttributeNotFound
from actl.signals import onSignal


class NativeFunction(AObject):
	def __init__(self, function):
		self._function = function
		super().__init__({})

		@onSignal('actl.Function:created', None)
		async def _onFunctionCreated(Function):
			self._head['__class__'] = Function

		if self.class_ is None:

			@onSignal('actl.Object:created')
			async def _onObjectCreated(Object):
				self._head['__class__'] = Object

	async def call(self, *args, **kwargs):
		return await self._function(*args, **kwargs)

	async def toPyString(self):
		return f'{type(self).__name__}({self._function})'

	async def apply(self, *args):
		return type(self)(AppliedFunction(self._function, *args))

	async def lookupSpecialAttribute(self, key):
		if key == '__call__':
			return self, True

		if key == 'apply':
			return NativeFunction(self.apply), True

		if key == 'name':
			return await self.String.call(self._function.__name__), True

		if key == 'signature':
			return self.emptySignature, True

		if key in ('body', 'scope'):
			return self.ANone, True

		if key == '__get__':
			raise AAttributeNotFound('__get__')

		return await super().lookupSpecialAttribute(key)

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False

		return self._function == other._function


@onSignal('actl.String:created')
async def _onStringCreated(String):
	NativeFunction.String = String


@onSignal('actl.Function:created')
async def _onFunctionCreated(_):
	from actl.objects.Function import Signature

	@onSignal('actl.Function:created')
	async def _onFunctionCreatedLastHandler(_):
		NativeFunction.emptySignature = await Signature.call(())


@onSignal('actl.None:created')
async def _onNoneCreated(ANone):
	NativeFunction.ANone = ANone
