from actl.objects.object import makeClass
from actl.objects.object.utils import addMethod


While = makeClass('While')


@addMethod(While, '__init__')
async def _While__init(self, conditionFrame, code=None):
	self.setAttribute('conditionFrame', conditionFrame)
	if code is not None:
		self.setAttribute('code', code)

	return self
