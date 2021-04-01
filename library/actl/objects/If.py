from actl.objects.object import makeClass
from actl.objects.object.utils import addMethodToClass


If = makeClass('If')
elif_ = makeClass('_Elif').call()
else_ = makeClass('_Else').call()


@addMethodToClass(If, '__call__')
def _(cls, ifCondition, *elifConditions, elseCode=None):
	self = cls.super_(If, '__call__').call()

	conditions = (ifCondition,) + elifConditions

	self.setAttribute('conditions', conditions)
	if elseCode is not None:
		self.setAttribute('elseCode', elseCode)

	return self
