class SlotsViaGetAttr:
	def __getattr__(self, key):
		raise NotImplementedError

	@property
	def __call__(self):
		return self.__getattr__('__call__')

	@property
	def __iter__(self):  # pylint: disable=non-iterator-returned
		return self.__getattr__('__iter__')

	@property
	def __getitem__(self):
		return self.__getattr__('__getitem__')

	@property
	def __setitem__(self):
		return self.__getattr__('__setitem__')

	@property
	def __delitem__(self):
		return self.__getattr__('__delitem__')

	@property
	def __contains__(self):
		return self.__getattr__('__contains__')

	@property
	def __bool__(self):
		return self.__getattr__('__bool__')

	@property
	def __repr__(self):
		return self.__getattr__('__repr__')

	@property
	def __str__(self):
		return self.__getattr__('__str__')


class Lazy(SlotsViaGetAttr):
	_default = object()

	def __init__(self, func):
		self._func = func
		super().__init__(self._default)

	def _evaluate(self):
		if self._value is not Lazy._default:
			return
		self._value = self._func()

	def __getattr__(self, key):
		self._evaluate()
		return super().__getattr__(key)
