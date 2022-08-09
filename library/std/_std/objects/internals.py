from actl.objects import NativeFunction, class_
from actl import executeSyncCoroutine


@NativeFunction
async def addMethod(cls, name, method):
	name = str(name)

	self_ = await cls.getAttribute('__self__')
	self_[name] = method


Iter = executeSyncCoroutine(class_.call('Iter'))


@Iter.addMethod('__init__')
async def _Iter__init(self, collection):
	head = await collection.getAttribute('_head')
	self._head = iter(head._value)


@Iter.addMethod('next')
async def _Iter__next(self):
	return next(self._head)
