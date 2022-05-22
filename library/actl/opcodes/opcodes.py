from .AnyOpCode import DynamicOpCode


VARIABLE = DynamicOpCode.create('VARIABLE', 'name')
SET_VARIABLE = DynamicOpCode.create('SET_VARIABLE', 'dst', 'src')
CALL_FUNCTION = DynamicOpCode.create(
	'CALL_FUNCTION', 'dst', 'function', typeb='(', args=[], kwargs={}
)
CALL_FUNCTION_STATIC = DynamicOpCode.create(
	'CALL_FUNCTION', 'dst', 'function', typeb='(', staticArgs=[], staticKwargs={}, args=[], kwargs={}
)

RETURN = DynamicOpCode.create('RETURN', 'var')
CALL_OPERATOR = DynamicOpCode.create('CALL_OPERATOR', 'dst', 'first', 'operator', 'second')
GET_ATTRIBUTE = DynamicOpCode.create('GET_ATTRIBUTE', 'dst', 'object', 'attribute')
SET_ATTRIBUTE = DynamicOpCode.create('SET_ATTRIBUTE', 'object', 'attribute', 'src')
