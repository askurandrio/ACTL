from actl.objects.object import class_
from actl.utils import executeSyncCoroutine


While = executeSyncCoroutine(class_.call('While'))


@While.addMethod('__init__')
async def _While__init(self, conditionFrame, code=None):
	await self.setAttribute('conditionFrame', conditionFrame)
	if code is not None:
		await self.setAttribute('code', code)

	return self
