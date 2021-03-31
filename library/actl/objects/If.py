from actl.objects.object import AObjectClass


If = AObjectClass('If')
elif_ = AObjectClass('_Elif').call()
else_ = AObjectClass('_Else').call()


@If.addMethodToClass('__call__')
def _(cls, ifCondition, *elifConditions, elseCode=None):
	self = cls.super_(If, '__call__').call()

	conditions = (ifCondition,) + elifConditions

	self.setAttribute('conditions', conditions)
	if elseCode is not None:
		self.setAttribute('elseCode', elseCode)

	return self
