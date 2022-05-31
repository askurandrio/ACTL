# pylint: disable=protected-access
from actl.objects.AToPy import AToPy
from actl.objects.object import makeClass
from actl.objects.object.utils import addMethod, addMethodToClass
from actl.utils import executeSyncCoroutine


Bool = makeClass('Bool')

Bool.True_ = executeSyncCoroutine(Bool.call())
Bool.True_._value = True

Bool.False_ = executeSyncCoroutine(Bool.call())
Bool.False_._value = False


@addMethodToClass(Bool, '__call__')
async def _Bool__call(_, val):
	if val in (Bool.True_, Bool.False_):
		return val

	toBoolMethod = await val.getAttribute(Bool)
	return await toBoolMethod.call()


@addMethod(Bool, AToPy)
async def _Bool__AToPy(self):
	return self._value
