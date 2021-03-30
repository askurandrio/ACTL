from actl.objects import AToPy
from actl.objects.object import BuildClass


NoneType = BuildClass('NoneType')
ANone = NoneType.call()


@NoneType.addMethodToClass('__call__')
def _(_):
	return ANone


@NoneType.addMethod(AToPy)
def _(_):
	return None
