
import copy
import itertools


class Buffer:
	def __init__(self, head=iter('')):
		self.__head = iter(head)
		self.__cache = []

	def proxy(self, idx_start):
		return BufferProxy(idx_start, self)

	def get(self, index, default=None):
		try:
			return self[index]
		except KeyError:
			return default

	def pop(self, index):
		self.load(index)
		return self.__cache.pop(index)

	def insert(self, index, elem):
		self.load(index)
		return self.__cache.insert(index, elem)

	def load(self, index):
		index -= len(self.__cache)
		if index >= 0:
			if index < 10:
				index = 10
			self.__cache.extend(itertools.islice(self.__head, None, index, None))

	def __getitem__(self, index):
		if isinstance(index, slice):
			if index.start is None:
				index_start = None
			else:
				index_start = index.start - len(self.__cache)
				if index_start < 0:
					index_start = None
			if index.stop is None:
				index_stop = None
			else:
				index_stop = index.stop - len(self.__cache)
				if index_stop < 0:
					index_stop = None
			it, self.__head = itertools.tee(self.__head, 2)
			result = self.__cache[index]
			result.extend(itertools.islice(it, index_start, index_stop, index.step))
			return type(self)(result)
		self.load(index)
		return self.__cache[index]

	def __setitem__(self, index, elem):
		if isinstance(index, slice):
			self.load(index.stop)
		self.__cache[index] = elem

	def __delitem__(self, index):
		if isinstance(index, slice):
			self.load(index.stop)
		else:
			self.load(index)
		del self.__cache[index]

	def __iter__(self):
		for idx in itertools.count():
			self.load(idx)
			try:
				yield self.__cache[idx]
			except IndexError as ex:
				return ex

	def __bool__(self):
		self.load(1)
		return bool(self.__cache)

	def __repr__(self):
		self.load(20)
		return f'Buffer<{self.__cache[:20]}>'


class BufferProxy:
	def __init__(self, idx_start, parent):
		self.__idx_start = idx_start
		self.__parent = parent

	def get(self, index):
		return self.__parent.get(self.calculate_index(index))

	def pop(self, index):
		return self.__parent.pop(self.calculate_index(index))

	def insert(self, index, elem):
		return self.__parent.insert(self.calculate_index(index), elem)

	def calculate_index(self, index):
		if isinstance(index, slice):
			index_start = None if index.start is None else self.__idx_start + index.start
			index_stop = None if index.stop is None else self.__idx_start + index.stop
			return slice(index_start, index.stop, index_stop)
		return self.__idx_start + index

	def __getitem__(self, index):
		return self.__parent[self.calculate_index(index)]

	def __setitem__(self, index, elem):
		self.__parent[self.calculate_index(index)] = elem

	def __delitem__(self, index):
		del self.__parent[self.calculate_index(index)]

	def __iter__(self):
		for idx in itertools.count(self.__idx_start):
			try:
				yield self.__parent[idx]
			except IndexError as ex:
				return ex

	def __bool__(self):
		return bool(self.__parent[self.calculate_index(1):])

	def __repr__(self):
		return f'BufferProxy<{self[:20]}>'
