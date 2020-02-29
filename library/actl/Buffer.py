import itertools


class Buffer:
	def __init__(self, head=''):
		self._buff = []
		self._head = iter(head)

	def watch(self, func):
		def watch(elem):
			func(elem)
			return elem

		return type(self)(map(watch, self))

	def set_(self, it):
		self._buff = []
		self._head = iter(it)

	def one(self):
		res, = self
		return res

	def pop(self, index=0):
		self._load(index)
		return self._buff.pop(index)

	def copy(self):
		buff, self._buff = self._buff, []
		self._head = itertools.chain(iter(buff), self._head)
		self._head, *res = itertools.tee(self._head, 2)
		return type(self)(res[0])

	def append(self, *items):  # pylint: disable=no-self-use
		self += items

	def startswith(self, tmpl):
		tmpl = list(tmpl)
		self._load(len(tmpl))
		return self._buff[:len(tmpl)] == tmpl

	def transaction(self):
		return _Transaction(self)

	def _load(self, quantity):
		if isinstance(quantity, slice):
			quantity = quantity.stop
		if (quantity is None) or (quantity < 0):
			self._buff.extend(self._head)
			return

		quantity = (quantity + 1) - len(self._buff)
		if quantity > 0:
			self._buff.extend(itertools.islice(self._head, None, quantity, None))

	def __eq__(self, other):
		return list(self) == list(other)

	def __getitem__(self, index):
		if isinstance(index, slice):
			res = itertools.islice(self.copy(), index.start, index.stop, index.step)
			return type(self)(res)
		self._load(index)
		return self._buff[index]

	def __delitem__(self, index):
		self._load(index)
		self._buff.__delitem__(index)

	def __iter__(self):
		self._head, head = itertools.tee(self._head)
		return itertools.chain(iter(self._buff), head)

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

	def __repr__(self):
		self._load(10)
		res = str(self._buff[:10])
		if len(self._buff) == 11:
			res = res[:-1] + ', ...]'
		return f'{type(self).__name__}({res})'

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
	def __init__(self, buff):
		self._buff = buff
		self._backup = None
		self._commit = False

	def commit(self):
		self._commit = True

	def __enter__(self):
		assert self._backup is None
		self._backup = self._buff.copy()
		return self

	def __exit__(self, *_):
		if not self._commit:
			self._buff.set_(self._backup)
