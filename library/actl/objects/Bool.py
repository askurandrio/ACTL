# pylint: disable=protected-access
from actl.objects.AToPy import AToPy
from actl.objects.object import makeClass
from actl.objects.object.Object import Object
from actl.objects.object.utils import addMethod, addMethodToClass


Bool = makeClass('Bool')

Bool.True_ = Bool.call()
Bool.True_._value = True

Bool.False_ = Bool.call()
Bool.False_._value = False


@addMethodToClass(Bool, '__call__')
def _(_, val):
	if val in (Bool.True_, Bool.False_):
		return val

	return val.getAttribute(Bool).call()


@addMethod(Bool, AToPy)
def _(self):
	return self._value
