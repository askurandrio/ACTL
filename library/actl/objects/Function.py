from actl.objects import makeClass, addMethod


Function = makeClass('Function')
Signature = makeClass('Signature')


@addMethod(Function, '__init__')
def _Function_init(self, name, signature, body):
	self.setAttribute('name', name)
	self.setAttribute('signature', signature)
	self.setAttribute('body', body)

	return self


@addMethod(Signature, '__init__')
def _Signature_init(self, args):
	self.setAttribute('args', args)
	return self
