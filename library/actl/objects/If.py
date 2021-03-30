from actl.objects.object import BuildClass


If = BuildClass('If')
elif_ = BuildClass('_Elif').call()
else_ = BuildClass('_Else').call()


@If.addMethodToClass('__call__')
def _(cls, ifCondition, *elifConditions, elseCode=None):
	self = cls.super_(If, '__call__').call()

	conditions = (ifCondition,) + elifConditions

	self.setAttribute('conditions', conditions)
	if elseCode is not None:
		self.setAttribute('elseCode', elseCode)

	return self
