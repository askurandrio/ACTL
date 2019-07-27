
class MetaAnyOpCode(type):
	__cache = {}

	def __eq__(self, item):
		if isinstance(item, self):
			return True
		if isinstance(item, type):
			return issubclass(item, self)
		return False

	def __call__(self, *args, **kwargs):
		inst = super().__call__(*args, **kwargs)
		key = str(inst)
		if key in self.__cache:
			return self.__cache[key]
		self.__cache[key] = inst
		return inst

	def __ne__(self, item):
		return not (self == item)

	def __hash__(self):
		return hash(repr(self))

	def __repr__(self):
		return f"opcodes.{self.__name__}"


class AnyOpCode(metaclass=MetaAnyOpCode): #pylint: disable=R0903

	def __eq__(self, item):
		return isinstance(item, type(self))

	def __ne__(self, item):
		return not (self == item)

	def __hash__(self):
		return hash(repr(self))

	def __repr__(self):
		return f'{self.__class__.__name__}({self.__dict__})'


class DynamicOpCode(AnyOpCode):
	__slots__ = ()

	def __init__(self, *args, **kwargs):
		for key, value in zip(self.__slots__, args):
			setattr(self, key, value)
		for key, value in kwargs.items():
			assert (not hasattr(self, key)), f'This attribute already exist: {key}, {self}'
			setattr(self, key, value)

	def __repr__(self):
		result = f'{self.__class__.__name__}('
		for key in self.__slots__:
			result += f'{key}={getattr(self, key)}, '
		if result[-2:] == ', ':
			result = result[:-2]
		result += ')'
		return result

	@classmethod
	def create(cls, name, *attributes):
		code_template = 'class {name}(DynamicOpCode):\n' \
							 '   __slots__ = ({attributes})\n'

		attributes = ', '.join(f'"{attribute}"' for attribute in attributes)
		if attributes:
			attributes += ','
		code = code_template.format(name=name,
											 attributes=attributes)
		lc_scope = {'DynamicOpCode':cls}
		exec(code, globals(), lc_scope) #pylint: disable=W0122
		return lc_scope[name]