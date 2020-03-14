from actl.utils.SlotsViaGetAttr import SlotsViaGetAttr


class Watch(SlotsViaGetAttr):
	def __init__(self, value, **handlers):
		self._value = value
		self._handlers = handlers

	def __getattr__(self, key):
		if key in self._handlers:
			self._handlers[key]()
		return getattr(self._value, key)
