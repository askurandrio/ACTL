from actl.objects.Bool import Bool
from actl.objects.BuildClass import BuildClass


Vector = BuildClass('Vector')


@Vector.addMethod(Bool)
def _(_):
	return Bool.False_
