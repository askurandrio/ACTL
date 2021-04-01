from actl.objects.object import makeClass
from actl.objects.object.utils import addMethodToClass
from actl.opcodes import RETURN


Function = makeClass('Function')
Signature = makeClass('Signature')


@addMethodToClass(Function, '__call__')
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


@addMethodToClass(Signature, '__call__')
def _(cls, args):
	self = cls.super_(Function, '__call__').call()

	self.setAttribute('args', args)
	return self
