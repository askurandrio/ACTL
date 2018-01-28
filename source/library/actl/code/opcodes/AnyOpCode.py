
class MetaAnyOpCode(type):
	def __eq__(self, item):
		if isinstance(item, self):
			return True
		if isinstance(item, type):
			return issubclass(item, self)
		return False

	def __ne__(self, item):
		return not (self == item)

	def __hash__(self):
		return hash(tuple(sorted(self.__dict__)))

	def __repr__(self):
		return f"opcodes.{self.__name__}"


class AnyOpCode(metaclass=MetaAnyOpCode): #pylint: disable=R0903

	def __eq__(self, item):
		return isinstance(item, type(self))

	def __ne__(self, item):
		return not (self == item)

	def __repr__(self):
		return f'{self.__class__.__name__}({self.__dict__})'
