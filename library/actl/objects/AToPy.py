from actl.objects.String import String
from actl.objects.object import AObject
from actl.utils import executeSyncCoroutine
from actl.objects.PyToA import PyToA


class _MetaAToPy(type):
	def __call__(self, value):
		if not isinstance(value, AObject):
			return value

		if executeSyncCoroutine(value.hasAttribute(PyToA)):
			toPyToAMethod = executeSyncCoroutine(value.getAttribute(PyToA))
			valuePyToA = executeSyncCoroutine(toPyToAMethod.call())
			return valuePyToA._value

		return super().__call__(value)


class AToPy(metaclass=_MetaAToPy):
	def __init__(self, value):
		self._value = value

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False

		return self._value == other._value

	def __repr__(self):
		return str(self)

	def __str__(self):
		toStringMethod = executeSyncCoroutine(self._value.getAttribute(String))
		aString = executeSyncCoroutine(toStringMethod.call())
		return type(self)(aString)
