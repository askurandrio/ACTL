from actl.objects.object import makeClass, addMethod, NativeFunction, Result
from actl.objects.String import String


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

	return appliedFunction


@addMethod(Function, String)
def _Function__String(self):
	name = self.getAttribute('name')
	args = ', '.join(self.getAttribute('signature').getAttribute('args'))
	return String.call(f'fun {name}({args})')


@addMethod(Signature, '__init__')
def _Signature_init(self, args):
	self.setAttribute('args', args)
	return self
