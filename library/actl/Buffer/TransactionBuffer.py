import itertools
from actl.Buffer.TransactionBufferOrigin import TransactionBufferOrigin


class TransactionBuffer:
	def __init__(self, origin):
		self._origin = origin
		self._skippedIndexes = set()

	@property
	def origin(self):
		return TransactionBufferOrigin(self._origin, self._shiftIndex(0))

	def commit(self):
		for index in reversed(sorted(self._skippedIndexes)):
			del self._origin[index]

	def pop(self, index=0):
		result = self[index]
		del self[index]
		return result

	def __getitem__(self, index):
		index = self._shiftIndex(index)
		return self._origin[index]

	def __delitem__(self, index):
		index = self._shiftIndex(index)
		if not isinstance(index, slice):
			index = slice(index, index + 1)
		for removeIndex in range(index.start, index.stop):
			self._skippedIndexes.add(removeIndex)

	def _shiftIndex(self, index):
		if isinstance(index,  slice):
			indexStart = 0 if index.start is None else index.start
			indexStart = self._shiftIndex(indexStart)

			indexStop = index.stop
			if indexStop is not None:
				indexStop = self._shiftIndex(indexStop)

			assert index.step is None

			return slice(indexStart, indexStop)

		shiftIndex = 0
		for realIndex in itertools.count():
			if realIndex in self._skippedIndexes:
				continue
			if shiftIndex == index:
				return realIndex
			shiftIndex += 1

	def __repr__(self):
		return f'{type(self).__name__}({self._origin[self._shiftIndex(0):self._shiftIndex(10)]})'

	def __bool__(self):
		try:
			self._origin[self._shiftIndex(0)]
		except IndexError:
			return False
		return True
