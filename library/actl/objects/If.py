from actl.objects.object import makeClass
from actl.objects.object.utils import addMethod
from actl.utils import executeSyncCoroutine


If = makeClass('If')
elif_ = executeSyncCoroutine(makeClass('_Elif').call())
else_ = executeSyncCoroutine(makeClass('_Else').call())


@addMethod(If, '__init__')
async def _If__init(self, ifCondition, *elifConditions, elseCode=None):
	conditions = (ifCondition,) + elifConditions

	self.setAttribute('conditions', conditions)
	if elseCode is not None:
		self.setAttribute('elseCode', elseCode)
