

class Scope:
	def __init__(self, head):
		self.__head = head

	def get(self, key, default=None):
		return self.__head.get(key, default)

	def update(self, head):
		self.__head.update(head)

	def __contains__(self, key):
		return key in self.__head

	def __getitem__(self, key):
		return self.__head[key]

	def __setitem__(self, key, value):
		self.__head[key] = value

	def __repr__(self):
		return f'Scope<{self.__head}>'
