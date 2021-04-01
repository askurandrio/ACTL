from actl.objects.Bool import Bool
from actl.objects.object import makeClass
from actl.objects.object.utils import addMethod, addMethodToClass


Vector = makeClass('Vector')


@addMethodToClass(Vector, '__call__')
def _(cls):
	self = cls.super_(Vector, '__call__').call()
	self._elements = []
	return self


@addMethod(Vector, 'append')
def _(self, element):
	self._elements.append(element)


@addMethod(Vector, Bool)
def _(self):
	return Bool.True_ if self._elements else Bool.False_
