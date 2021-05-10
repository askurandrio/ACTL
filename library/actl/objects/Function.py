from actl.objects.object import makeClass, addMethod, NativeFunction
from actl.Result import Result


Function = makeClass('Function')
Signature = makeClass('Signature')
type(Function).Function = Function


@addMethod(Function, '__init__')
def _Function_init(self, name, signature, body, scope):
	self.setAttribute('name', name)
	self.setAttribute('signature', signature)
	self.setAttribute('body', body)
	self.setAttribute('scope', scope)

	return self


@addMethod(Function, 'apply')
def _Function_apply(self, *applyArgs):
	@NativeFunction
	def appliedFunction(*args):
		return self.call(*applyArgs, *args)

	return Result.fromObj(appliedFunction)


@addMethod(Signature, '__init__')
def _Signature_init(self, args):
	self.setAttribute('args', args)
	return self
