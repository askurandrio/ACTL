
import copy
import itertools


class Buffer:
	def __init__(self, head=iter('')):
		self.__head = iter(head)
		self.__cache = []

	def pop(self, index):
		self.load(index)
		return self.__cache.pop(index)

	def load(self, length):
		while length >= len(self.__cache):
			self.__next()

	def insert(self, index, element):
		try:
			self.load(index)
		except StopIteration:
			if len(self.__cache) == index:
				self.__cache.append(element)
			else:
				raise IndexError(f'This index not found: {index}')
		self.__cache.insert(index, element)

	def update(self, other):
		self.__cache = other.__cache
		self.__head = other.__head

	def __next(self):
		self.__cache.append(next(self.__head))

	def __add__(self, other):
		result = self.__class__()
		result += self
		result += other
		return result

	def __iadd__(self, other=None):
		args = self.__cache, self.__head
		if other is not None:
			args += other.__cache, other.__head
		self.__head = itertools.chain(*args)
		self.__cache = []
		return self

	def __getitem__(self, index):
		if isinstance(index, slice):
			self.__iadd__()
			copy_self = copy.deepcopy(self)
			head = itertools.islice(copy_self.__head, index.start, index.stop, index.step)
			return type(self)(head)
		else:
			self.load(index)
			return self.__cache[index]

	def __iter__(self):
		return self

	def __next__(self):
		if self.__cache:
			return self.__cache.pop(0)
		return next(self.__head)

	def __bool__(self):
		try:
			element = next(self)
		except StopIteration:
			return False
		else:
			self.insert(0, element)
			return True

	def __deepcopy__(self, _=None):
		self.__iadd__()
		self.__head, copy_head = itertools.tee(self.__head, 2)
		return type(self)(head=copy_head)
	 
	@classmethod
	def create(cls, *args):
		return cls(args)

	@classmethod
	def generator(cls, func):
		def temp(*args, **kwargs):
			result = func(*args, **kwargs)
			return cls(result)
		return temp

	def __repr__(self):
		return f'Buffer<{repr(list(copy.deepcopy(self)[:5]))}>'
