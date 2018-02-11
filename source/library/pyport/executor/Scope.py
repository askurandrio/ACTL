
import actl


class Scope:
	def __init__(self):
		self.__head = {}

	def update(self, scope):
		it = scope if isinstance(scope, type(self)) else scope.items()
		for key, value in it:
			self[key] = value

	def get(self, key, default=None):
		return self.__head.get(key, default)

	def __getitem__(self, key):
		return self.__head[key]

	def __setitem__(self, key, value):
		self.__head[key] = value

	def __delitem__(self, key):
		del self.__head[key]
