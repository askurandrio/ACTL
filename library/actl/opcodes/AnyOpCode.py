
class MetaAnyOpCode(type):
	def __eq__(self, item):
		if isinstance(item, self):
			return True
		if isinstance(item, type):
			return issubclass(item, self)
		return False

	def __ne__(self, item):
		return not self == item

	def __hash__(self):
		return hash(repr(self))

	def __repr__(self):
		return f"opcodes.{self.__name__}"


class AnyOpCode(metaclass=MetaAnyOpCode):  # pylint: disable=R0903
	def __ne__(self, item):
		return not self == item

	def __hash__(self):
		return hash(repr(self))

	def __repr__(self):
		return f'{self.__class__.__name__}({self.__dict__})'


class DynamicOpCode(AnyOpCode):
	__slots__ = ()
	_defaults = {}

	def __init__(self, *args, **kwargs):
		args = dict(zip(self.__slots__, args))

		diff = set(args) & set(kwargs)
		assert not diff, f'These attributes have multiply declaration: {diff}'

		kwargs = {
			**self._defaults,
			**args,
			**kwargs
		}

		diff = set(self.__slots__) - set(kwargs)
		assert not diff, f'These attributes not declared: {diff}'

		for key, value in kwargs.items():
			setattr(self, key, value)

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
			for key in sorted(self.__slots__)
			if key not in self._defaults.keys()
		)
		notDefaultAttributesToStr = ', '.join(
			f'{key}={attributes[key]!r}'
			for key in self._defaults.keys()
			if self._defaults[key] == attributes[key]
		)
		if notDefaultAttributesToStr:
			attributesToStr += f', {notDefaultAttributesToStr}'
		return '{}({})'.format(type(self).__name__, attributesToStr)

	@classmethod
	def create(cls, name, *attributes, **defaults):
		attributes = cls.__slots__ + attributes + tuple(defaults.keys())
		defaults = {**cls._defaults, **defaults}
		class_ = type(name, (cls,), {'__slots__': attributes, '_defaults': defaults})
		return class_
