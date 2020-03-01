# pylint: disable=unexpected-special-method-signature


class Lazy:
	_default = object()

	def __init__(self, func):
		self._func = func
		self._val = self._default

	def _evaluate(self):
		if self._val is not self._default:
			return
		self._val = self._func()

	def __getattr__(self, key):
		self._evaluate()
		return getattr(self._val, key)

	@property
	def __call__(self):
		return self.__getattr__('__call__')

	@property
	def __iter__(self):
		return self.__getattr__('__iter__')

	@property
	def __getitem__(self):
		return self.__getattr__('__getitem__')

	@property
	def __setitem__(self):
		return self.__getattr__('__setitem__')\

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
