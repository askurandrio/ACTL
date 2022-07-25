from actl.objects.object import class_
from actl.utils import executeSyncCoroutine


If = executeSyncCoroutine(class_.call('If'))
elif_ = executeSyncCoroutine(executeSyncCoroutine(class_.call('_Elif')).call())
else_ = executeSyncCoroutine(executeSyncCoroutine(class_.call('_Else')).call())


@If.addMethod('__init__')
async def _If__init(self, ifCondition, *elifConditions, elseCode=None):
	conditions = (ifCondition,) + elifConditions

	await self.setAttribute('conditions', conditions)
	if elseCode is not None:
		await self.setAttribute('elseCode', elseCode)
