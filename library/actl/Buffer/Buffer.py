import itertools


class Buffer:
	def __init__(self, head=()):
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
		self._load(index)
		self._buff[index:index] = list(items)

	def append(self, *items):  # pylint: disable=no-self-use
		self += items

	def startswith(self, tmpl):
		tmpl = list(tmpl)
		self._load(len(tmpl))
		return self._buff[:len(tmpl)] == tmpl

	def _load(self, quantity):
		if isinstance(quantity, slice):
			quantity = quantity.stop

		if (quantity is None) or (quantity < 0):
			self._buff.extend(self._head)

		quantity = (quantity + 1) - len(self._buff)
		for _ in range(quantity):
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

	def reprElements(self):
		self._load(10)
		elementsAsStr = str(self._buff[:10])
		if len(self._buff) == 11:
			elementsAsStr = elementsAsStr[:-1] + ', ...]'
		return elementsAsStr

	def __repr__(self):
		return f'{type(self).__name__}({self.reprElements()})'

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
