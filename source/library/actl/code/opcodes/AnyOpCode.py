
class MetaAnyOpCode(type):
	def __eq__(self, item):
		return isinstance(item, self) or (isinstance(item, type) and issubclass(self, item))

	def __ne__(self, item):
		return not (self == item)

	def __repr__(self):
		return f"opcodes.{self.__name__}"


class AnyOpCode(metaclass=MetaAnyOpCode): #pylint: disable=R0903

	def __eq__(self, item):
		return isinstance(item, AnyOpCode)

	def __ne__(self, item):
		return not (self == item)

	def __repr__(self):
		return f'{self.__class__.__name__}({self.__dict__})'
