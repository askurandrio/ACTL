from actl.objects import AToPy
from actl.objects.object import AObjectClass


NoneType = AObjectClass('NoneType')
ANone = NoneType.call()


@NoneType.addMethodToClass('__call__')
def _(_):
	return ANone


@NoneType.addMethod(AToPy)
def _(_):
	return None
