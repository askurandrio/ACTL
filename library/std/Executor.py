
import actl
from actl.objects import While, Object, PyToA


class Executor:
	_HANDLERS = {}

	def __init__(self, code, scope):
		self.scope = scope
		self.lastValue = None

		self.execute(code)

	def execute(self, code):
		for opcode in code:
			handler = self._HANDLERS[type(opcode)]
			self.lastValue = handler(self, opcode)

	@classmethod
	def _addHandler(cls, opcode):
		def decorator(handler):
			cls._HANDLERS[opcode] = handler
		return decorator


@Executor._addHandler(type(Object))
def _(executor, opcode):
	assert opcode.getAttr('__class__').equal(While)

	while True:
		executor.execute(opcode.getAttr('conditionFrame'))
		assert executor.lastValue.equal(PyToA.fromPy(True))
		executor.execute(opcode.getAttr('code'))


@Executor._addHandler(actl.opcodes.VARIABLE)
def _(executor, opcode):
	return executor.scope[opcode.name]


@Executor._addHandler(actl.opcodes.CALL_FUNCTION_STATIC)
def _(executor, opcode):
	function = executor.scope[opcode.function]
	assert opcode.typeb == '('
	executor.scope[opcode.dst] = function.call(*opcode.args, **opcode.kwargs)


@Executor._addHandler(actl.opcodes.CALL_FUNCTION)
def _(executor, opcode):
	function = executor.scope[opcode.function]
	assert opcode.typeb == '('
	args = (executor.scope[key] for key in opcode.args)
	kwargs = {key: executor.scope[key] for key in opcode.kwargs}
	executor.scope[opcode.dst] = function.call(*args, **kwargs)
