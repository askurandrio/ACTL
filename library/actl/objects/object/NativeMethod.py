# pylint: disable=arguments-differ, useless-super-delegation
from actl.objects.object.AObject import AObject


class NativeMethod(AObject):
	def __init__(self, rawMethod):
		@NativeFunction
		async def get(aSelf):
			return NativeFunction(self._rawMethod).apply(aSelf)

		super().__init__({})
		self._rawMethod = rawMethod
		self._get = get

	@property
	def class_(self):
		return AObject.Object

	async def lookupSpecialAttribute(self, key):
		if key == '__get__':
			return self, True

		return await super().lookupSpecialAttribute(key)

	async def get(self, instance):
		return await self._get.call(instance)

	async def toPyString(self):
		return f'{type(self).__name__}({self._rawMethod})'


class NativeFunction(AObject):
	def __init__(self, function):
		self._function = function
		super().__init__({})

	@property
	def class_(self):
		return AObject.Object

	async def call(self, *args, **kwargs):
		return await self._function(*args, **kwargs)

	async def toPyString(self):
		return f'{type(self).__name__}({self._function})'

	def apply(self, *args):
		return type(self)(_AppliedFunction(self._function, *args))

	async def lookupSpecialAttribute(self, key):
		if key == '__call__':
			return self, True

		return await super().lookupSpecialAttribute(key)

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False
		return self._function == other._function


class _AppliedFunction:
	def __init__(self, function, *args):
		self._function = function
		self._args = args

	async def __call__(self, *args, **kwargs):
		return await self._function(*self._args, *args, **kwargs)

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
