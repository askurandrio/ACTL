from actl.objects import AToPy
from actl.objects.object import makeClass, Result
from actl.objects.object.utils import addMethod, addMethodToClass


NoneType = makeClass('NoneType')
ANone = NoneType.call().obj


@addMethodToClass(NoneType, '__call__')
def _(_):
	return Result.fromObj(ANone)


@addMethod(NoneType, AToPy)
def _(_):
	return None
