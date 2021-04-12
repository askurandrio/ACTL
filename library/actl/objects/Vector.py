from actl.Result import Result
from actl.objects.Bool import Bool
from actl.objects.object import makeClass
from actl.objects.object.utils import addMethod, addMethodToClass


Vector = makeClass('Vector')


@addMethodToClass(Vector, '__call__')
def _(cls):
	resultSelf = cls.super_.obj(Vector, '__call__').obj.call.obj()
	resultSelf.obj._elements = []
	return resultSelf


@addMethod(Vector, 'append')
def _(self, element):
	self._elements.append(element)
	return Result(obj=None)


@addMethod(Vector, Bool)
def _(self):
	return Result(obj=Bool.True_) if self._elements else Result(obj=Bool.False_)
