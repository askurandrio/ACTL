from actl.objects.object import makeClass
from actl.objects.object.utils import addMethodToClass


While = makeClass('While')


@addMethodToClass(While, '__call__')
def _(cls, conditionFrame, code=None):
	resultSelf = cls.super_(While, '__call__').call()

	resultSelf.obj.setAttribute('conditionFrame', conditionFrame)
	if code is not None:
		resultSelf.obj.setAttribute('code', code)

	return resultSelf
