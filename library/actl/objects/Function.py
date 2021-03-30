from actl.objects.object import BuildClass
from actl.opcodes import RETURN


Function = BuildClass('Function')
Signature = BuildClass('Signature')


@Function.addMethodToClass('__call__')
def _(cls, name, signature, body):
	self = cls.super_(Function, '__call__').call()

	self.setAttribute('name', name)
	self.setAttribute('signature', signature)
	if RETURN != body[-1]:
		body += (
			RETURN('None'),
		)
	self.setAttribute('body', body)

	return self


@Signature.addMethodToClass('__call__')
def _(cls, args):
	self = cls.super_(Function, '__call__').call()

	self.setAttribute('args', args)
	return self
