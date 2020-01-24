
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
		kwargs = {**self._defaults, **kwargs}
		for key, value in zip(self.__slots__, args):
			setattr(self, key, value)
		for key, value in kwargs.items():
			assert (not hasattr(self, key)), f'This attribute already exist: {key}, {self}'
			setattr(self, key, value)

	def _getAttributes(self):
		return {key: getattr(self, key) for key in self.__slots__}

	def __eq__(self, other):
		if type(self) != type(other):  # pylint: disable=unidiomatic-typecheck
			return False
		return self._getAttributes() == other._getAttributes()

	def __repr__(self):
		attributes = ', '.join(f'{key}={value!r}' for key, value in self._getAttributes().items())
		return '{}({})'.format(type(self).__name__, attributes)

	@classmethod
	def create(cls, name, *attributes, **defaults):
		attributes = cls.__slots__ + attributes
		defaults = {**cls._defaults, **defaults}
		class_ = type(name, (cls,), {'__slots__': attributes, '_defaults': defaults})
		return class_
