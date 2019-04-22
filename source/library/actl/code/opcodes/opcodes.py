
from .AnyOpCode import DynamicOpCode


class Making(DynamicOpCode):
	__slots__ = ('opcode',)

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False
		return self.opcode == other.opcode #pylint: disable=E1101


VARIABLE = DynamicOpCode.create('VARIABLE', 'name')
PASS = DynamicOpCode.create('PASS')
JUMP = DynamicOpCode.create('JUMP', 'label')
RETURN = DynamicOpCode.create('RETURN', 'var')
SAVE_CODE = DynamicOpCode.create('SAVE_CODE', 'function')
SET_VARIABLE = DynamicOpCode.create('SET_VARIABLE', 'dst', 'src')
BUILD_STRING = DynamicOpCode.create('BUILD_STRING', 'dst', 'string')
BUILD_NUMBER = DynamicOpCode.create('BUILD_NUMBER', 'dst', 'number')
CALL_OPERATOR = DynamicOpCode.create('CALL_OPERATOR', 'dst', 'operator', 'args')
CALL_FUNCTION = DynamicOpCode.create('CALL_FUNCTION', 'dst', 'function', 'typeb', 'args', 'kwargs')
