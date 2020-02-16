# pylint: disable=protected-access
from actl.objects.AToPy import AToPy
from actl.objects.BuildClass import BuildClass


Number = BuildClass('Number')


@Number.addMethodToClass('__call__')
def _(cls, value):
	self = cls.getAttr('__super__').getAttr('__call__').call()
	if isinstance(value, str):
		if '.' in value:
			value = float(value)
		else:
			value = int(value)
	self._value = value
	return self


@Number.addMethod(AToPy)
def _(self):
	return self._value
