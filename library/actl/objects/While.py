from actl.objects.object import makeClass
from actl.objects.object.utils import addMethodToClass


While = makeClass('While')


@addMethodToClass(While, '__call__')
def _While__call(cls, conditionFrame, code=None):
	resultSelf = cls.super_(While, '__call__').call()

	resultSelf.setAttribute('conditionFrame', conditionFrame)
	if code is not None:
		resultSelf.setAttribute('code', code)

	return resultSelf
