from actl.Result import Result
from actl.objects import AToPy
from actl.objects.object import makeClass
from actl.objects.object.utils import addMethod, addMethodToClass


NoneType = makeClass('NoneType')
ANone = NoneType.call.obj().obj


@addMethodToClass(NoneType, '__call__')
def _(_):
	return Result(obj=ANone)


@addMethod(NoneType, AToPy)
def _(_):
	return None
