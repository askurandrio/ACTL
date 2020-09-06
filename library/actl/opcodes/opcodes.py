from .AnyOpCode import DynamicOpCode


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
		num = cls.counter()
		return cls(f'__IV{num}')


SET_VARIABLE = DynamicOpCode.create('SET_VARIABLE', 'dst', 'src')
CALL_FUNCTION = DynamicOpCode.create(
	'CALL_FUNCTION', 'dst', 'function', typeb='(', args=[], kwargs={}
)
CALL_FUNCTION_STATIC = CALL_FUNCTION.create('CALL_FUNCTION_STATIC')

RETURN = DynamicOpCode.create('RETURN', 'var')
CALL_OPERATOR = DynamicOpCode.create('CALL_OPERATOR', 'dst', 'first', 'operator', 'second')
