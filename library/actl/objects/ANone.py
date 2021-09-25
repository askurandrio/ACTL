from actl.objects import AToPy
from actl.objects.object import makeClass, executeSyncCoroutine
from actl.objects.object.utils import addMethod, addMethodToClass


NoneType = makeClass('NoneType')
ANone = executeSyncCoroutine(NoneType.call())


@addMethodToClass(NoneType, '__call__')
async def _NoneType__call(_):
	return ANone


@addMethod(NoneType, AToPy)
async def __NoneType__AToPy(_):
	return None
