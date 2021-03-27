# pylint: disable=protected-access
from actl.objects.AToPy import AToPy
from actl.objects.BuildClass import BuildClass


Bool = BuildClass('Bool')

Bool.True_ = Bool.call()
Bool.True_._value = True

Bool.False_ = Bool.call()
Bool.False_._value = False


@Bool.addMethodToClass('__call__')
def _(_, val):
	if val in (Bool.True_, Bool.False_):
		return val

	return val.getAttr(Bool).call()


@Bool.addMethod(AToPy)
def _(self):
	return self._value
