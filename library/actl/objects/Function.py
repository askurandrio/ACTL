from actl.objects.object import makeClass, addMethod, NativeFunction
from actl.objects.String import String
from actl.utils import executeSyncCoroutine
from actl.signals import triggerSignal


Function = makeClass('Function')
Signature = makeClass('Signature')


@addMethod(Function, '__init__')
async def _Function_init(self, name, signature, body, scope):
	await self.setAttribute('name', name)
	await self.setAttribute('signature', signature)
	await self.setAttribute('body', body)
	await self.setAttribute('scope', scope)

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
	body = await self.getAttribute('body')
	args = ', '.join(signatureArgs)
	return await String.call(f'fun {name}({args}): {body}')


@addMethod(Signature, '__init__')
async def _Signature_init(self, args):
	await self.setAttribute('args', args)


executeSyncCoroutine(triggerSignal('actl.Function:created', Function))
