from actl.objects.Bool import Bool
from actl.objects.BuildClass import BuildClass


Vector = BuildClass('Vector')


@Vector.addMethodToClass('__call__')
def _(cls):
	self = cls.super_(Vector, '__call__').call()
	self._elements = []
	return self


@Vector.addMethod('append')
def _(self, element):
	self._elements.append(element)


@Vector.addMethod(Bool)
def _(self):
	return Bool.True_ if self._elements else Bool.False_
