
class Scope:
	def __init__(self):
		self.__head = {}

	def __getitem__(self, key):
		return self.__head[key]

	def __setitem__(self, key, value):
		self.__head[key] = value

	def __delitem__(self, key):
		del self.__head[key]
