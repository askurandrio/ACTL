
from .AnyOpCode import DynamicOpCode


class Making(DynamicOpCode):
	__slots__ = ('opcode',)

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False
		return self.opcode == other.opcode  # pylint: disable=E1101


class VARIABLE(DynamicOpCode):
	__slots__ = ('name',)
	__counts = 10
	
	@classmethod
	def temp(cls):
		cls.__counts += 1
		return cls(f'__IV{cls.__counts}')


END_LINE = DynamicOpCode.create('END_LINE')()
SET_VARIABLE = DynamicOpCode.create('SET_VARIABLE', 'dst', 'src')
BUILD_STRING = DynamicOpCode.create('BUILD_STRING', 'dst', 'string')
BUILD_NUMBER = DynamicOpCode.create('BUILD_NUMBER', 'dst', 'number')
CALL_FUNCTION = DynamicOpCode.create('CALL_FUNCTION', 'dst', 'function', 'typeb', 'args', 'kwargs')

PASS = DynamicOpCode.create('PASS')
JUMP = DynamicOpCode.create('JUMP', 'label')
RETURN = DynamicOpCode.create('RETURN', 'var')
SAVE_CODE = DynamicOpCode.create('SAVE_CODE', 'function')
CALL_OPERATOR = DynamicOpCode.create('CALL_OPERATOR', 'dst', 'operator', 'args')
