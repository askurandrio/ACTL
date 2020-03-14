from actl.objects.BuildClass import BuildClass
from actl.opcodes import RETURN


Function = BuildClass('Function')


@Function.addMethodToClass('__call__')
def _(cls, name, signature, body):
	self = cls.super_(Function, '__call__').call()

	self.setAttr('name', name)
	self.setAttr('signature', signature)
	if RETURN != body[-1]:
		body += (
			RETURN('None'),
		)
	self.setAttr('body', body)

	return self
