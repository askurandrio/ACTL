from actl.objects import PyToA
from actl.objects.object import class_
from actl.signals import triggerSignal
from actl.utils import executeSyncCoroutine


ANoneType = executeSyncCoroutine(class_.call('NoneType'))
ANone = executeSyncCoroutine(ANoneType.call())


@ANoneType.addMethodToClass('__call__')
async def _NoneType__call(_):
	return ANone


@ANoneType.addMethod(PyToA)
async def __NoneType__PyToA(_):
	return await PyToA.call(None)


executeSyncCoroutine(triggerSignal('actl.None:created', ANone))
