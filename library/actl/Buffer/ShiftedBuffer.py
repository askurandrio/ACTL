from actl.Buffer.ShiftedBufferOrigin import ShiftedBufferOrigin


class ShiftedBuffer:
	def __init__(self, origin):
		self._origin = origin
		self.indexShift = 0

	@property
	def origin(self):
		return ShiftedBufferOrigin(self._origin, self.indexShift)

	def pop(self):
		element, = self.shift()
		return element

	def shift(self, shift=1):
		result = self[:shift]
		self.indexShift += shift
		return result

	def delShift(self):
		del self._origin[:self.indexShift]

	def __getitem__(self, index):
		index = self._shiftIndex(index)
		return self._origin[index]

	def __delitem__(self, index):
		index = self._shiftIndex(index)
		del self._origin[index]

	def _shiftIndex(self, index):
		if isinstance(index,  slice):
			if index.start is not None:
				indexStart = self.indexShift + index.start
			else:
				indexStart = self.indexShift
			indexStop = index.stop
			if indexStop is not None:
				indexStop += self.indexShift
			assert index.step is None
			return slice(indexStart, indexStop)

		return self.indexShift + index

	def __repr__(self):
		return f'{type(self).__name__}({self._origin[self.indexShift:self.indexShift+10]})'

	def __bool__(self):
		try:
			self._origin[self.indexShift]
		except IndexError:
			return False
		return True
