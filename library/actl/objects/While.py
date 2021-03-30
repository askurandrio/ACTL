from actl.objects.object import BuildClass


While = BuildClass('While')


@While.addMethodToClass('__call__')
def _(cls, conditionFrame, code=None):
	self = cls.super_(While, '__call__').call()

	self.setAttribute('conditionFrame', conditionFrame)
	if code is not None:
		self.setAttribute('code', code)

	return self
