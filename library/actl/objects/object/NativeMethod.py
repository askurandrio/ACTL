# pylint: disable=arguments-differ, useless-super-delegation
from actl.objects.object.AObject import AObject


class NativeMethod(AObject):
	def __init__(self, rawMethod):
		@NativeFunction
		def get(aSelf):
			return NativeFunction(self._rawMethod).apply(aSelf)

		super().__init__({})
		self._rawMethod = rawMethod
		self._get = get

	@property
	def class_(self):
		from actl.objects.object import Object

		return Object

	@property
	def get(self):
		return self._get

	def toPyString(self):
		return f'{type(self).__name__}({self._rawMethod})'


class NativeFunction(AObject):
	def __init__(self, function):
		self._function = function
		super().__init__({})

	@property
	def class_(self):
		from actl.objects.object import Object

		return Object

	@property
	def call(self):
		return self._function

	def toPyString(self):
		return f'{type(self).__name__}({self._function})'

	def apply(self, *args):
		return type(self)(_AppliedFunction(self._function, *args))

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False
		return self._function == other._function


class _AppliedFunction:
	def __init__(self, function, *args):
		self._function = function
		self._args = args

	def __call__(self, *args, **kwargs):
		return self._function(*self._args, *args, **kwargs)

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False

		return (
			(self._function == other._function) and
			(self._args == other._args)
		)

	def __repr__(self):
		return str(self)

	def __str__(self):
		args = ', '.join(str(arg) for arg in (self._function,) + self._args)
		return f'{type(self).__name__}({args})'
