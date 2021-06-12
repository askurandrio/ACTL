default = object()


def asDecorator(func):
	def decorator(functionForDecorate):
		return func(functionForDecorate)

	return decorator


class DeclaredClass:
	__slots__ = ()
	_defaults = {}

	def __init__(self, *args, **kwargs):
		for idx, value in enumerate(args):
			setattr(self, self.__slots__[idx], value)

		for name, value in kwargs.items():
			assert not hasattr(self, name), \
				f'Attribute<{name}> already declared as {getattr(self, name)}'
			setattr(self, name, value)

		for name, value in self._defaults.items():
			if hasattr(self, name):
				continue
			setattr(self, name, value)

		for name in self.__slots__:
			assert hasattr(self, name), \
				f'Attribute<{name}> should be declared'

	def _getAttributes(self):
		return {key: getattr(self, key) for key in self.__slots__}

	def __eq__(self, other):
		if type(self) != type(other):  # pylint: disable=unidiomatic-typecheck
			return False
		return self._getAttributes() == other._getAttributes()

	def __repr__(self):
		attributes = self._getAttributes()
		attributesToStr = ', '.join(
			repr(attributes[key])
			for key in self.__slots__
			if key not in self._defaults
		)
		notDefaultAttributesToStr = ', '.join(
			f'{key}={attributes[key]!r}'
			for key in self._defaults
			if self._defaults[key] != attributes[key]
		)
		if notDefaultAttributesToStr:
			attributesToStr += f', {notDefaultAttributesToStr}'
		return '{}({})'.format(type(self).__name__, attributesToStr)

	@classmethod
	def create(cls, name, *attributes, **defaults):
		attributes = cls.__slots__ + attributes + tuple(defaults)
		defaults = {**cls._defaults, **defaults}
		class_ = type(name, (cls,), {'__slots__': attributes, '_defaults': defaults})
		return class_
