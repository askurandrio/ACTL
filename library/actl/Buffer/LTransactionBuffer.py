from actl.Buffer.ShiftedBuffer import ShiftedBuffer


class LTransactionBuffer:
	def __init__(self, origin):
		self._origin = origin
		self._shiftIndex = 0

	def pop(self):
		elem = self._origin[self._shiftIndex]
		self._shiftIndex += 1
		return elem

	def commit(self):
		del self._origin[:self._shiftIndex]

	@property
	def origin(self):
		return ShiftedBuffer(self._origin, self._shiftIndex)

	@property
	def _shiftedOrigin(self):
		return self._origin[self._shiftIndex:]

	def __getitem__(self, item):
		return self._shiftedOrigin[item]

	def __delitem__(self, item):
		self._shiftIndex += item.stop
		assert item.start is item.step is None

	def __bool__(self):
		return bool(self._shiftedOrigin)

	def __repr__(self):
		return f'{type(self).__name__}({self._shiftedOrigin.reprElements()})'
