class ShiftedBufferOrigin:
	def __init__(self, origin, shift):
		self._origin = origin
		self._shift = shift

	def startsWith(self, tmpl):
		return self._origin[self._shift:].startsWith(tmpl)

	def pop(self, index=0):
		return self._origin.pop(self._shift + index)

	def insert(self, index, elems):
		self._origin.insert(index + self._shift, elems)

	def __getitem__(self, index):
		if isinstance(index, slice):
			assert index.step is index.stop is None
			return self._origin[(index.start + self._shift):]
		return self._origin[index + self._shift]

	def __delitem__(self, index):
		if index.start is not None:
			indexStart = self._shift + index.start
		else:
			indexStart = self._shift
		indexStop = index.stop
		if indexStop is not None:
			indexStop += self._shift	

		assert index.step is None

		del self._origin[slice(indexStart, indexStop)]

	def __repr__(self):
		return f'{type(self).__name__}({self._origin[self._shift:]})'

	def __bool__(self):
		return bool(self._origin[self._shift:])
