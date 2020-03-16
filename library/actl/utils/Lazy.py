from actl.utils.SlotsViaGetAttr import SlotsViaGetAttr


class Lazy(SlotsViaGetAttr):
	_default = object()

	def __init__(self, func):
		self._func = func
		self._value = self._default

	def _evaluate(self):
		if self._value is not Lazy._default:
			return
		self._value = self._func()

	def __getattr__(self, key):
		self._evaluate()
		return getattr(self._value, key)
