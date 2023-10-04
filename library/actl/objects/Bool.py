from actl.objects.object import class_
from actl.objects.String import String
from actl.utils import executeSyncCoroutine
from actl.signals import onSignal


Bool = executeSyncCoroutine(class_.call('Bool'))

Bool.True_ = executeSyncCoroutine(Bool.call())
Bool.True_._value = True

Bool.False_ = executeSyncCoroutine(Bool.call())
Bool.False_._value = False


@Bool.addMethodToClass('__call__')
async def _Bool__call(_, val):
	if val in (Bool.True_, Bool.False_):
		return val

	toBoolMethod = await val.getAttribute(Bool)
	return await toBoolMethod.call()


@onSignal('actl.PyToA:created')
async def _onPyToACreated(PyToA):
	@Bool.addMethod(PyToA)
	async def _Bool__PyToA(self):
		return await PyToA.call(self._value)


@String.addMethod(Bool)
async def _String__Bool(self):
	return Bool.True_ if self.value else Bool.False_
