class TransactionBufferOrigin:
	def __init__(self, origin, shift):
		self._origin = origin
		self._shift = shift

	def startsWith(self, tmpl):
		tmpl = self._origin[: self._shift] + tmpl
		return self._origin.startsWith(tmpl)

	def pop(self, index=0):
		return self._origin.pop(self._shift + index)

	def insert(self, index, elems):
		self._origin.insert(index + self._shift, elems)

	def __getitem__(self, index):
		index = self._shiftIndex(index)
		return self._origin[index]

	def _shiftIndex(self, index):
		if isinstance(index, slice):
			if index.start is not None:
				indexStart = self._shift + index.start
			else:
				indexStart = self._shift
			indexStop = index.stop
			if indexStop is not None:
				indexStop += self._shift
			assert index.step is None
			return slice(indexStart, indexStop)

		return self._shift + index

	def __delitem__(self, index):
		index = self._shiftIndex(index)

		del self._origin[index]

	def __repr__(self):
		return f'{type(self).__name__}({self._origin[self._shift:self._shift+10]})'

	def __bool__(self):
		try:
			self._origin[self._shift]
		except IndexError:
			return False
		return True
