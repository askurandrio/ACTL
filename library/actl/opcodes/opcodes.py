from .AnyOpCode import DynamicOpCode


VARIABLE = DynamicOpCode.create('VARIABLE', 'name')
SET_VARIABLE = DynamicOpCode.create('SET_VARIABLE', 'dst', 'src', srcStatic=None)
CALL_FUNCTION = DynamicOpCode.create(
	'CALL_FUNCTION', 'dst', 'function', typeb='(', args=[], kwargs={}
)
CALL_FUNCTION_STATIC = CALL_FUNCTION.create('CALL_FUNCTION_STATIC')

RETURN = DynamicOpCode.create('RETURN', 'var')
CALL_OPERATOR = DynamicOpCode.create('CALL_OPERATOR', 'dst', 'first', 'operator', 'second')
GET_ATTRIBUTE = DynamicOpCode.create('GET_ATTRIBUTE', 'dst', 'object', 'attribute')
