from .AnyOpCode import DynamicOpCode


class Making(DynamicOpCode):
	__slots__ = ('opcode',)

	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return False
		return self.opcode == other.opcode  # pylint: disable=E1101


class _Counter:
	def __init__(self, count):
		self._init = count
		self._count = self._init

	def reset(self):
		self._count = self._init

	def __call__(self):
		self._count += 1
		return self._count


class VARIABLE(DynamicOpCode):
	__slots__ = ('name',)
	counter = _Counter(10)

	@classmethod
	def temp(cls):
		t = cls.counter()
		return cls(f'__IV{t}')


SET_VARIABLE = DynamicOpCode.create('SET_VARIABLE', 'dst', 'src')
CALL_FUNCTION = DynamicOpCode.create(
	'CALL_FUNCTION', 'dst', 'function', typeb='(', args=[], kwargs={}
)
CALL_FUNCTION_STATIC = CALL_FUNCTION.create('CALL_FUNCTION_STATIC')

PASS = DynamicOpCode.create('PASS')
JUMP = DynamicOpCode.create('JUMP', 'label')
RETURN = DynamicOpCode.create('RETURN', 'var')
SAVE_CODE = DynamicOpCode.create('SAVE_CODE', 'function')
CALL_OPERATOR = DynamicOpCode.create('CALL_OPERATOR', 'dst', 'operator', 'args')
