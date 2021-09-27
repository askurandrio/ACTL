from actl.objects.String import String
from actl.objects.object import Object, executeSyncCoroutine


class _MetaAToPy(type):
	def __call__(self, value):
		if not isinstance(value, type(Object)):
			return value

		if executeSyncCoroutine(value.hasAttribute(AToPy)):
			toAToPyMethod = executeSyncCoroutine(value.getAttribute(AToPy))
			return executeSyncCoroutine(toAToPyMethod.call())

		return super().__call__(value)


class AToPy(metaclass=_MetaAToPy):
	def __init__(self, value):
		self._value = value

	def __repr__(self):
		return str(self)

	def __str__(self):
		toStringMethod = executeSyncCoroutine(self._value.getAttribute(String))
		aString = executeSyncCoroutine(toStringMethod.call())
		return type(self)(aString)
