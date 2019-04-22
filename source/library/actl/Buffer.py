import copy
import itertools


class Buffer:
	def __init__(self, head=iter('')):
		self._buff = []
		self._head = iter(head)
	
	def pop(self, index):
		self._load(index)
		return self._buff.pop(index)

	def copy(self, quantity=1):
		buff, self._buff = self._buff, []
		self._head = itertools.chain(iter(buff), self._head)
		self._head, *res = itertools.tee(self._head, quantity+1)
		if quantity == 1:
			return type(self)(res[0])
		return [type(self)(head) for head in res]

	def extract(self):
		while self:
			yield self.pop(0)

	def _load(self, quantity):
		quantity -= len(self._buff)
		if quantity > 0:
			self._buff.extend(itertools.islice(self._head, None, quantity, None))

	def __getitem__(self, index):
		if isinstance(index, slice):
			tmp = self.copy()
			tmp._head = itertools.islice(tmp._head, index.start, index.stop, index.step)
			return tmp
		self._load(index)
		return self._buff[index]

	def __setitem__(self, index, elem):
		if isinstance(index, slice):
			self._load(index.stop)
		self._buff[index] = elem

	def __delitem__(self, index):
		if isinstance(index, slice):
			self._load(index.stop)
		else:
			self._load(index)
		del self._buff[index]

	def __iter__(self):
		return itertools.chain(iter(self._buff), self._head)

	def __bool__(self):
		self._load(1)
		return bool(self._buff)

	def __repr__(self):
		l = self.copy(20)[:10]
		return f'{type(self).__name__}<{self.__cache[:20]}>'

	@classmethod
	def of(cls, func):
		def wrapper(*args, **kwargs):
			return cls(func(*args, **kwargs))
		return wrapper
