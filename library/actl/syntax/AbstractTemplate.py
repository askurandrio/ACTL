class AbstractTemplate:
	__slots__ = ('arg',)

	def __init__(self, *args, **kwargs):
		kwargs.setdefault('arg', None)
		kwargs.update(zip(self.__slots__, args))
		for key, value in kwargs.items():
			setattr(self, key, value)
		for key in self.__slots__:
			assert hasattr(self, key), f'{self} has no attribute {key}'

	def __call__(self, parser, inp):
		raise NotImplementedError

	def __repr__(self):
		args = ', '.join(str(getattr(self, key)) for key in self.__slots__)
		return f'{type(self).__name__}({args})'
