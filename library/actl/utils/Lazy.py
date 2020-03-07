from contextlib import contextmanager

from actl.utils.SlotsViaGetAttr import SlotsViaGetAttr


@contextmanager
def setAttrForBlock(obj, attr, value):
	# pylint: disable=unexpected-special-method-signature, invalid-overridden-method
	prevValue = getattr(obj, attr)
	setattr(obj, attr, value)
	yield
	setattr(obj, attr, prevValue)


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
