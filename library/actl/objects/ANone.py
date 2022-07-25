from actl.objects import AToPy
from actl.objects.object import class_
from actl.signals import triggerSignal
from actl.utils import executeSyncCoroutine


ANoneType = executeSyncCoroutine(class_.call('NoneType'))
ANone = executeSyncCoroutine(ANoneType.call())


@ANoneType.addMethodToClass('__call__')
async def _NoneType__call(_):
	return ANone


@ANoneType.addMethod(AToPy)
async def __NoneType__AToPy(_):
	return None


executeSyncCoroutine(triggerSignal('actl.None:created', ANone))
