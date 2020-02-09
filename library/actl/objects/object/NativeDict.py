from actl.objects.object.exceptions import AKeyNotFound
from actl.objects.object.NativeClass import NativeClass


class NativeDict(NativeClass):
	def __init__(self, initHead):
		super().__init__()
		self._head = initHead

	def setItem(self, key, value):
		self._head[key] = value

	def getItem(self, key):
		try:
			return self._head[key]
		except KeyError:
			raise AKeyNotFound(key=key)

	def __str__(self):
		return f'{type(self).__name__}<{self._head}>'
