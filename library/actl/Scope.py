

class Scope:
	def __init__(self, head):
		self.__head = head

	def get(self, key, default=None):
		return self.__head.get(key, default)

	def __contains__(self, key):
		return key in self.__head

	def __getitem__(self, key):
		return self.__head[key]

	def __setitem__(self, key, value):
		self.__head[key] = value

	def __repr__(self):
		return f'Scope<{self.__head}>'


class __ScopeChild(Scope):
	def __init__(self, parent):
		self.__parent = parent
		super().__init__({})

	def __contains__(self, key):
		if key in self.__parent:
			return True
		return super().__contains__(key)

	def __getitem__(self, key):
		if key in self.__parent:
			return self.__parent[key]
		return super().__getitem__(key)

	def __setitem__(self, key, value):
		if key in self.__parent:
			raise RuntimeError('not allowed')
		return super().__setitem__(key, value)

	def __delitem__(self, key):
		if key in self.__parent:
			raise RuntimeError('not allowed')
		return super().__detitem__(key)
