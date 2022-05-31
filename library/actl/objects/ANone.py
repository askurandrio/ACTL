from actl.objects import AToPy
from actl.objects.object import makeClass, addMethod, addMethodToClass
from actl.signals import triggerSignal
from actl.utils import executeSyncCoroutine


ANoneType = makeClass('NoneType')
ANone = executeSyncCoroutine(ANoneType.call())


@addMethodToClass(ANoneType, '__call__')
async def _NoneType__call(_):
	return ANone


@addMethod(ANoneType, AToPy)
async def __NoneType__AToPy(_):
	return None


executeSyncCoroutine(triggerSignal('actl.None:created', ANone))
