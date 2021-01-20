import itertools


class Buffer:
	_emptyIter = iter(())

	def __init__(self, head=_emptyIter):
		self._buff = []
		self._head = iter(head)

	@property
	def origin(self):
		return self

	def watch(self, func):
		def watch(elem):
			func(elem)
			return elem

		return type(self)(map(watch, self))

	def one(self):
		res, = self
		return res

	def pop(self, index=0):
		self._load(index)
		return self._buff.pop(index)

	def insert(self, index, items):
		if index != 0:
			self._load(index)
		self._buff[index:index] = list(items)

	def append(self, *items):  # pylint: disable=no-self-use
		self += items

	def startswith(self, tmpl):
		tmpl = list(tmpl)
		self._load(len(tmpl))
		return self._buff[:len(tmpl)] == tmpl

	def loadAll(self):
		self._buff.extend(self._head)
		self._head = self._emptyIter
		return self

	def _load(self, index):
		if isinstance(index, slice):
			index = index.stop

		assert not (
			(
				(index is None) or (index < 0)
			) and (
				self._head is not self._emptyIter
			)
		), 'use .loadAll() if you want load index with undefined count to load'

		index = (index + 1) - len(self._buff)

		for _ in range(index):
			try:
				self._buff.append(next(self._head))
			except StopIteration:
				break

	def __eq__(self, other):
		return list(self) == list(other)

	def __getitem__(self, index):
		if not isinstance(index, slice):
			self._load(index)
			return self._buff[index]

		def gen():
			for elem in self._head:
				self._buff.append(elem)
				yield elem

		res = itertools.chain(iter(self._buff), gen())
		return Buffer(itertools.islice(res, index.start, index.stop, index.step))

	def __delitem__(self, index):
		self._load(index)
		del self._buff[index]

	def __iter__(self):
		yield from self._buff

		for elem in self._head:
			self._buff.append(elem)
			yield elem

	def __iadd__(self, other):
		self._head = itertools.chain(iter(self._head), iter(other))
		return self

	def __add__(self, other):
		res = type(self)()
		res += self
		res += other
		return res

	def __bool__(self):
		self._load(0)
		return bool(self._buff)

	def reprElements(self, sep=None):
		if sep is None:
			sep = ', '

		self._load(10)
		elementsAsStr = '['
		elementsAsStr += sep.join(repr(elem) for elem in self._buff[:10])
		if len(self._buff) == 11:
			elementsAsStr += f'{sep}...'
		elementsAsStr += ']'
		return elementsAsStr

	def __repr__(self, sep=None):
		return f'{type(self).__name__}({self.reprElements(sep)})'

	def __str__(self):
		return self.__repr__('\n')

	@classmethod
	def of(cls, *it):
		return cls(it)

	@classmethod
	def wrap(cls, func):
		def wrapper(*args, **kwargs):
			return cls(func(*args, **kwargs))
		return wrapper

	@classmethod
	def inf(cls):
		@cls.wrap
		def gen():
			value = 0
			while True:
				yield value
				value += 1

		return gen()


class _Transaction:
	def __init__(self):
		self.isCommited = False

	def commit(self):
		self.isCommited = True
