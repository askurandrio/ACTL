
from .AnyOpCode import AnyOpCode


class DynamicOpCode(AnyOpCode):
	_attributes = ()

	def __init__(self, *args, **kwargs):
		for key, value in zip(self._attributes, args):
			setattr(self, key, value)
		for key, value in kwargs.items():
			assert (not hasattr(self, key)), f'This attribute already exist: {key}, {self}'
			setattr(self, key, value)

	def __repr__(self):
		result = f'{self.__class__.__name__}('
		for key in self._attributes:
			result += f'{key}={getattr(self, key)}, '
		if result[-2:] == ', ':
			result = result[:-2]
		result += ')'
		return result

	@classmethod
	def create(cls, name, *attributes):
		code_template = 'class {name}(DynamicOpCode):\n' \
							 '   _attributes = ({attributes},)\n'
		code = code_template.format(name=name,
											 attributes=', '.join(f'"{attribute}"' for attribute in attributes))
		lc_scope = {'DynamicOpCode':cls}
		exec(code, globals(), lc_scope) #pylint: disable=W0122
		return lc_scope[name]


class Making(DynamicOpCode):
	_attributes = ('opcode',)

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False
		return self.opcode == other.opcode #pylint: disable=E1101


class VARIABLE(DynamicOpCode):
	__count_temp = 0
	_attributes = ('name',)

	@classmethod
	def get_temp(cls, count=None):
		if count is not None:
			return [cls.get_temp() for _ in range(count)]
		cls.__count_temp += 1
		return cls(name=f'__IV{cls.__count_temp}')


CTUPLE = DynamicOpCode.create('CTUPLE', 'type', 'args', 'kwargs')
SET_VARIABLE = DynamicOpCode.create('SET_VARIABLE', 'out', 'source')
BUILD_STRING = DynamicOpCode.create('BUILD_STRING', 'out', 'string')
BUILD_NUMBER = DynamicOpCode.create('BUILD_NUMBER', 'out', 'number')
CALL_FUNCTION = DynamicOpCode.create('CALL_FUNCTION', 'out', 'function', 'type', 'args', 'kwargs')
