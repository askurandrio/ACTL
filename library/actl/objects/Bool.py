# pylint: disable=protected-access
from actl.objects.AToPy import AToPy
from actl.objects.BuildClass import BuildClass


Bool = BuildClass('Bool')

ATrue = Bool.call()
ATrue._value = True

AFalse = Bool.call()
AFalse._value = False


@Bool.addMethodToClass('__call__')
def _(_, val):
	if val in (ATrue, AFalse):
		return val

	return val.getAttr(Bool).call()


@Bool.addMethod(AToPy)
def _(self):
	return AToPy(self._value)
