from actl.objects.BuildClass import BuildClass


While = BuildClass('While')


@While.addMethodToClass('__call__')
def _(cls, conditionFrame, code=None):
	self = cls.super_(While, '__call__').call()

	self.setAttr('conditionFrame', conditionFrame)
	if code is not None:
		self.setAttr('code', code)

	return self
