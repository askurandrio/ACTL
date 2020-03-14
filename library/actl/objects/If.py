from actl.objects.BuildClass import BuildClass


If = BuildClass('If')
elif_ = BuildClass('_Elif').call()
else_ = BuildClass('_Else').call()


@If.addMethodToClass('__call__')
def _(cls, ifCondition, *elifConditions, elseCode=None):
	self = cls.super_(If, '__call__').call()

	conditions = (ifCondition,) + elifConditions

	self.setAttr('conditions', conditions)
	if elseCode is not None:
		self.setAttr('elseCode', elseCode)

	return self
