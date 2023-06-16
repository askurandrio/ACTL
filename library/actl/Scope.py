from actl.objects import AObject


class Scope:
	def __init__(self, head):
		self._head = head

	def child(self):
		return ScopeChild(self)

	def get(self, key, default=None):
		return self._head.get(key, default)

	def __contains__(self, key):
		return key in self._head

	def __getitem__(self, key):
		if key == '__scope__':
			return self

		return self._head[key]

	def __setitem__(self, key, value):
		assert isinstance(
			value, AObject
		), f'{type(value)}({value}) should be instance of AObject to be able to write in Scope'

		if key == '_':
			return

		self._head[key] = value

	def __repr__(self):
		reprHead = ', '.join(tuple(self._head.keys())[:3])
		if len(self._head) > 3:
			reprHead += ', ...'
		return f'Scope<{reprHead}>'


class ScopeChild(Scope):
	allowOverride = False  # TODO: improve this situation

	def __init__(self, parent):
		self._parent = parent
		super().__init__({})

	def getDiff(self):
		for key, value in self._head.items():
			if key.startswith('_tmpVar'):
				continue
			yield key, value

	def get(self, key, default=None):
		default = self._parent.get(key, default=default)
		return super().get(key, default=default)

	def __contains__(self, key):
		if key in self._parent:
			return True
		return super().__contains__(key)

	def __getitem__(self, key):
		try:
			return super().__getitem__(key)
		except KeyError:
			pass

		return self._parent[key]

	def __setitem__(self, key, value):
		if (not self.allowOverride) and (key in self._parent):
			raise RuntimeError(
				f'{key} is already defined in parent as {self._parent[key]}'
			)
		super().__setitem__(key, value)

	def __repr__(self):
		return f'ScopeChild<{self._parent}, {self._head}>'
