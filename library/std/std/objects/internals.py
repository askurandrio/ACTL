from actl.objects import NativeFunction, class_, ANone, String
from actl import executeSyncCoroutine


@NativeFunction
async def addMethod(cls, name, method):
	if await String.isinstance_(name):
		name = str(name)

	self_ = await cls.getAttribute('__self__')
	self_[name] = method
	return ANone


Iter = executeSyncCoroutine(class_.call('Iter'))


@Iter.addMethod('__init__')
async def _Iter__init(self, collection):
	if hasattr(collection, '_value'):
		collection = collection._value
	else:
		collection = (await collection.getAttribute('_head'))._value
	self._head = iter(collection)


@Iter.addMethod('next')
async def _Iter__next(self):
	return next(self._head)
