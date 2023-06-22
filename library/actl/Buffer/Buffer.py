import inspect
import itertools
from collections.abc import Iterator


class Buffer:
	_emptyIter = iter(())

	def __init__(self, head=_emptyIter):
		self._buff = []
		self._head = iter(head)

		if isinstance(head, (tuple, list, range)):
			self.loadAll()

	def watch(self, func):
		def watch(elem):
			func(elem)
			return elem

		return type(self)(map(watch, self))

	def filter(self, func):
		return type(self)(filter(func, self))

	def one(self):
		try:
			(res,) = self
		except ValueError as ex:
			raise ValueError(f'len({self}) != 1') from ex
		return res

	def pop(self, index=0):
		self._load(index)
		return self._buff.pop(index)

	def insert(self, index, items):
		loadIndex = index - 1
		if loadIndex > 0:
			self._load(loadIndex)
		self._buff[index:index] = list(items)

	def append(self, *items):
		self += items

	def startsWith(self, tmpl):
		tmpl = list(tmpl)
		self._load(len(tmpl))
		return self._buff[: len(tmpl)] == tmpl

	def loadAll(self):
		self._buff.extend(self._head)
		self._head = self._emptyIter
		return self

	def _load(self, index):
		if self._head is self._emptyIter:
			return

		if isinstance(index, slice):
			index = index.stop
			if index is None:
				index = -1

			if index > 0:
				index -= 1

		assert (
			index >= 0
		), 'use .loadAll() if you want load index with undefined count to load'

		index = (index + 1) - len(self._buff)

		for _ in range(index):
			try:
				self._buff.append(next(self._head))
			except StopIteration:
				break

	def __eq__(self, other):
		if not hasattr(other, '__iter__'):
			return False

		return list(self) == list(other)

	def __getitem__(self, index):
		self._load(index)
		res = self._buff[index]
		if isinstance(index, slice):
			return Buffer(res)
		return res

	def __delitem__(self, index):
		if isinstance(index, slice):
			indexStop = None if index.stop is None else index.stop - 1
			loadIndex = slice(index.start, indexStop, index.step)
		else:
			loadIndex = index

		self._load(loadIndex)
		del self._buff[index]

	def __iter__(self):
		yield from self._buff

		for elem in self._head:
			self._buff.append(elem)
			yield elem

	def __iadd__(self, other):
		if (self._head is self._emptyIter) and (not isinstance(other, Iterator)):
			self._buff.extend(other)
			return self

		self._head = itertools.chain(iter(self._head), iter(other))
		return self

	def __add__(self, other):
		res = type(self)(self)
		res += other
		return res

	def __bool__(self):
		self._load(0)
		return bool(self._buff)

	def __repr__(self):
		return str(self)

	def __str__(self):
		# self._load(10)
		elementsAsStr = '['
		elementsAsStr += ', '.join(repr(elem) for elem in self._buff[:10])
		if len(self._buff) == 11:
			elementsAsStr += ', ...'
		elementsAsStr += ']'
		return f'{type(self).__name__}({elementsAsStr})'

	@classmethod
	def of(cls, *it):
		return cls(it)

	@classmethod
	def wrap(cls, func):
		def wrapper(*args, **kwargs):
			result = func(*args, **kwargs)

			if inspect.iscoroutine(result):
				result = result.__await__()

			return cls(result)

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

	@classmethod
	async def loadAsync(cls, gen):
		head = []

		async for element in gen:
			head.append(element)

		return cls(head)
