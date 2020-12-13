from actl.objects.BuildClass import BuildClass


Operator = BuildClass('Operator')


@Operator.addMethodToClass('__call__')
def _(cls, operator):
	self = cls.super_(Operator, '__call__').call()
	self.setAttr('_operator', operator)
	return self
