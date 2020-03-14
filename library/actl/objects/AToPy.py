from actl.objects.String import String
from actl.objects.object import AbstractObject


class _MetaAToPy(type):
	def __call__(self, value):
		if not isinstance(value, AbstractObject):
			return value

		if value.hasAttr(AToPy):
			return value.getAttr(AToPy).call()

		return super().__call__(value)


class AToPy(metaclass=_MetaAToPy):
	def __init__(self, value):
		self._value = value

	def __str__(self):
		res = self._value.getAttr(String).call()
		return type(self)(res)
