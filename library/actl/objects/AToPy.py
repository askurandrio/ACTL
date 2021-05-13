from actl.objects.String import String
from actl.objects.object import Object


class _MetaAToPy(type):
	def __call__(self, value):
		if not isinstance(value, type(Object)):
			return value

		if value.hasAttribute(AToPy):
			return value.getAttribute(AToPy).call()

		return super().__call__(value)


class AToPy(metaclass=_MetaAToPy):
	def __init__(self, value):
		self._value = value

	def __repr__(self):
		return str(self)

	def __str__(self):
		res = self._value.getAttribute(String).call()
		return type(self)(res)
