# pylint: disable=protected-access
from actl.Result import Result
from actl.objects.AToPy import AToPy
from actl.objects.object import makeClass
from actl.objects.object.utils import addMethod, addMethodToClass


Bool = makeClass('Bool')

Bool.True_ = Bool.call.obj().obj
Bool.True_._value = True

Bool.False_ = Bool.call.obj().obj
Bool.False_._value = False


@addMethodToClass(Bool, '__call__')
def _(_, val):
	if val in (Bool.True_, Bool.False_):
		return Result(obj=val)

	return val.getAttribute.obj(Bool).obj.call.obj()


@addMethod(Bool, AToPy)
def _(self):
	return self._value
