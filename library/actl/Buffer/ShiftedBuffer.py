from actl.Buffer.ShiftedBufferOrigin import ShiftedBufferOrigin


class ShiftedBuffer:
	def __init__(self, origin):
		self._origin = origin
		self.indexShift = 0

	@property
	def origin(self):
		return ShiftedBufferOrigin(self._origin, self.indexShift)

	def pop(self):
		res = self[0]
		self.shift()
		return res

	def shift(self, shift=1):
		self.indexShift += shift

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
			indexStart = index.start
			if indexStart is not None:
				indexStart += self.indexShift
			indexStop = index.stop
			if indexStop is not None:
				indexStop += self.indexShift
			assert index.step is None
			return slice(indexStart, indexStop)

		return self.indexShift + index

	def __repr__(self):
		return f'{type(self).__name__}({self._origin[self.indexShift:]})'

	def __bool__(self):
		return bool(self._origin[self.indexShift:])
