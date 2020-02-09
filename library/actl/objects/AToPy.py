from actl.objects.Object import Object


class _MetaAToPy(type):
	def __call__(self, value):
		if not isinstance(value, type(Object)):
			return value

		if value.hasAttr(AToPy):
			return value.getAttr(AToPy).call()

		return super().__call__(value)


class AToPy(metaclass=_MetaAToPy):
	def __init__(self, value):
		self._value = value

	def __str__(self):
		res = self._value.getAttr('__toStr__').call()
		return type(self)(res)
