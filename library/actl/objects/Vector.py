from actl.Result import Result
from actl.objects.Bool import Bool
from actl.objects.object import makeClass
from actl.objects.object.utils import addMethod, addMethodToClass


Vector = makeClass('Vector')


@addMethodToClass(Vector, '__call__')
def _(cls):
	resultSelf = cls.super_(Vector, '__call__').call()
	resultSelf.obj._elements = []
	return resultSelf


@addMethod(Vector, 'append')
def _(self, element):
	self._elements.append(element)
	return Result.fromObj(None)


@addMethod(Vector, Bool)
def _(self):
	return Result.fromObj(Bool.True_) if self._elements else Result.fromObj(Bool.False_)
