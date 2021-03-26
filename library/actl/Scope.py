

class Scope:
	def __init__(self, head):
		self._head = head

	def child(self):
		return _ScopeChild(self)

	def get(self, key, default=None):
		return self._head.get(key, default)

	def __contains__(self, key):
		return key in self._head

	def __getitem__(self, key):
		return self._head[key]

	def __setitem__(self, key, value):
		self._head[key] = value

	def __repr__(self):
		reprHead = ', '.join(tuple(self._head.keys())[:3])
		if len(self._head) > 3:
			reprHead += ', ...'
		return f'Scope<{reprHead}>'


class _ScopeChild(Scope):
	def __init__(self, parent):
		self._parent = parent
		super().__init__({})

	def get(self, key, default=None):
		if key in self._parent:
			return self._parent[key]
		return super().get(key, default)

	def __contains__(self, key):
		if key in self._parent:
			return True
		return super().__contains__(key)

	def __getitem__(self, key):
		if key in self._parent:
			return self._parent[key]
		return super().__getitem__(key)

	def __setitem__(self, key, value):
		if key in self._parent:
			raise RuntimeError
		super().__setitem__(key, value)

	def __repr__(self):
		return f'ScopeChild<{self._parent}, {self._head}>'
