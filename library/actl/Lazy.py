# pylint: disable=unexpected-special-method-signature
import sys
from contextlib import contextmanager
from functools import partial
from traceback import format_stack


@contextmanager
def setAttrForBlock(obj, attr, value):
	prevValue = getattr(obj, attr)
	setattr(obj, attr, value)
	yield
	setattr(obj, attr, prevValue)


class SlotsViaGetAttr:
	def __init__(self, value):
		self._value = value

	def __getattr__(self, key):
		return getattr(self._value, key)

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
		return self.__getattr__('__setitem__')

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
