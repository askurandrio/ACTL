import itertools


class Buffer:
	def __init__(self, head=iter('')):
		self._buff = []
		self._head = iter(head)
	
	def get(self, index):
		self._load(index)
		return self._buff[index]

	def pop(self, index=0):
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
			yield self.pop()

	def set(self, other):
		self._buff = []
		self._head = iter(other)

	def index(self, value):
		for idx, elem in enumerate(self):
			if elem == value:
				return idx
		raise IndexError(f'Cant search this value: {value}')

	def append(self, *items):
		self += items

	def startswith(self, tmpl):
		tmpl = list(tmpl)
		src = list(self[:len(tmpl)])
		return src == tmpl

	def _load(self, quantity):
		quantity = (quantity + 1) - len(self._buff)
		if quantity > 0:
			self._buff.extend(itertools.islice(self._head, None, quantity, None))

	def __eq__(self, other):
		return list(self) == list(other)

	def __getitem__(self, index):
		if isinstance(index, slice):
			if (index.stop is not None) and (index.stop < len(self._buff)):
				return self._buff[index]
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

	def __contains__(self, value):
		try:
			self.index(value)
		except IndexError:
			return False
		else:
			return True

	def __iter__(self):
		yield from iter(self._buff)
		self._head, head = itertools.tee(self._head)
		yield from head

	def __iadd__(self, other):
		self._head = itertools.chain(iter(self._head), iter(other))
		return self

	def __add__(self, other):
		return type(self)(itertools.chain(iter(self), iter(other)))

	def __bool__(self):
		self._load(1)
		return bool(self._buff)

	def __repr__(self):
		lst = list(self[:11])
		res = str(lst[:10])
		if len(lst) == 11:
			res = res[:-1] + ', ...]'
		return f'{type(self).__name__}({res})'

	@classmethod
	def of(cls, *it):
		return cls(it)

	@classmethod
	def make(cls, func):
		def wrapper(*args, **kwargs):
			return cls(func(*args, **kwargs))
		return wrapper
