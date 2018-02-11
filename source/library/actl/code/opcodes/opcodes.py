
from .AnyOpCode import AnyOpCode, DynamicOpCode


class Making(DynamicOpCode):
	__slots__ = ('opcode',)

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False
		return self.opcode == other.opcode #pylint: disable=E1101


PASS = DynamicOpCode.create('PASS')
CARGS = DynamicOpCode.create('CARGS', 'args', 'kwargs')
RETURN = DynamicOpCode.create('RETURN', 'var')
READ_ATTR = DynamicOpCode.create('READ_ATTR', 'out', 'obj', 'attr')
BUILD_CODE = DynamicOpCode.create('BUILD_CODE', 'function')
SET_VARIABLE = DynamicOpCode.create('SET_VARIABLE', 'out', 'source')
BUILD_STRING = DynamicOpCode.create('BUILD_STRING', 'out', 'string')
BUILD_NUMBER = DynamicOpCode.create('BUILD_NUMBER', 'out', 'number')
CALL_FUNCTION = DynamicOpCode.create('CALL_FUNCTION', 'out', 'function', 'typeb', 'args', 'kwargs')
