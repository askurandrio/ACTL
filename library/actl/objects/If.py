from actl.objects.object import makeClass
from actl.objects.object.utils import addMethodToClass


If = makeClass('If')
elif_ = makeClass('_Elif').call().obj
else_ = makeClass('_Else').call().obj


@addMethodToClass(If, '__call__')
def _(cls, ifCondition, *elifConditions, elseCode=None):
	resultSelf = cls.super_(If, '__call__').obj.call()

	conditions = (ifCondition,) + elifConditions

	resultSelf.obj.setAttribute('conditions', conditions)
	if elseCode is not None:
		resultSelf.obj.setAttribute('elseCode', elseCode)

	return resultSelf
