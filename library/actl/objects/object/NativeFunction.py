from actl.objects.object.AObject import AObject
from actl.objects.object._AppliedFunction import AppliedFunction
from actl.objects.object.exceptions import AAttributeNotFound
from actl.signals import onSignal, triggerSignal
from actl.utils import executeSyncCoroutine


class NativeFunction(AObject):
	def __init__(self, function):
		self._function = function
		super().__init__({})

	async def _resolve__class__(self):
		try:
			return self.class_
		except AttributeError:
			return self.Object

	async def call(self, *args, **kwargs):
		return await self._function(*args, **kwargs)

	async def toPyString(self):
		return f'{type(self).__name__}({self._function})'

	async def apply(self, *args):
		return type(self)(AppliedFunction(self._function, *args))

	async def _resolve__call__(self):
		return self

	async def _resolve_apply(self):
		return NativeFunction(self.apply)

	async def _resolve_name(self):
		return await self.String.call(self._function.__name__)

	async def _resolve_signature(self):
		return self.emptySignature

	async def _resolve_body(self):
		return self.ANone

	async def _resolve_scope(self):
		return self.ANone

	@staticmethod
	async def _resolve__get__():
		raise AAttributeNotFound('__get__')

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False

		return self._function == other._function

	@classmethod
	async def isinstance_(cls, obj):
		return isinstance(obj, cls)


executeSyncCoroutine(triggerSignal('actl.NativeFunction:created', NativeFunction))


@onSignal('actl.String:created')
async def _onStringCreated(String):
	NativeFunction.String = String


@onSignal('actl.Function:created')
async def _onFunctionCreated(_):
	from actl.objects.object import class_
	from actl.objects.Function import Function, Signature

	# First, set class_ to Function to allow class_ stuff works
	NativeFunction.class_ = Function

	NativeFunction.class_ = await class_.call('NativeFunction', (Function,))

	NativeFunction.emptySignature = await Signature.call(())


@onSignal('actl.Object:created')
async def _onObjectCreated(Object):
	NativeFunction.Object = Object


@onSignal('actl.None:created')
async def _onNoneCreated(ANone):
	NativeFunction.ANone = ANone
