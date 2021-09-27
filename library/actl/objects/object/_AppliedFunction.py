class AppliedFunction:
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
