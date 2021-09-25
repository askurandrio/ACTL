from actl.objects.object import makeClass, addMethod, NativeFunction
from actl.objects.String import String


Function = makeClass('Function')
Signature = makeClass('Signature')
type(Function).Function = Function


@addMethod(Function, '__init__')
async def _Function_init(self, name, signature, body, scope):
	self.setAttribute('name', name)
	self.setAttribute('signature', signature)
	self.setAttribute('body', body)
	self.setAttribute('scope', scope)

	return self


@addMethod(Function, 'apply')
async def _Function_apply(self, *applyArgs):
	@NativeFunction
	async def appliedFunction(*args):
		return await self.call(*applyArgs, *args)

	return appliedFunction


@addMethod(Function, String)
async def _Function__String(self):
	name = await self.getAttribute('name')
	signature = await self.getAttribute('signature')
	signatureArgs = await signature.getAttribute('args')
	args = ', '.join(signatureArgs)
	return await String.call(f'fun {name}({args})')


@addMethod(Signature, '__init__')
async def _Signature_init(self, args):
	self.setAttribute('args', args)
	return self
