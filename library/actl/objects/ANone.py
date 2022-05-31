from actl.objects import AToPy
from actl.objects.object import makeClass
from actl.utils import executeSyncCoroutine
from actl.objects.object.utils import addMethod, addMethodToClass


ANoneType = makeClass('NoneType')
ANone = executeSyncCoroutine(ANoneType.call())


@addMethodToClass(ANoneType, '__call__')
async def _NoneType__call(_):
	return ANone


@addMethod(ANoneType, AToPy)
async def __NoneType__AToPy(_):
	return None
