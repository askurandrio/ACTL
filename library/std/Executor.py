
import actl
from actl.objects import While, Object, Bool
from actl.objects.AToPy import AToPy


class Executor:
	_HANDLERS = {}

	def __init__(self, code, scope):
		self.scope = scope

		self.execute(code)

	def execute(self, code):
		for opcode in code:
			print(opcode)
			handler = self._HANDLERS[type(opcode)]
			handler(self, opcode)

	@classmethod
	def _addHandler(cls, opcode):
		def decorator(handler):
			cls._HANDLERS[opcode] = handler
		return decorator


@Executor._addHandler(type(Object))  # pylint: disable=protected-access
def _(executor, opcode):
	assert opcode.getAttr('__class__').equal(While)

	def condition():
		executor.execute(opcode.getAttr('conditionFrame'))
		res = executor.scope['_']
		res = Bool.call(res)
		return AToPy(res)

	breakpoint()
	while condition():
		executor.execute(opcode.getAttr('code'))


@Executor._addHandler(actl.opcodes.VARIABLE)  # pylint: disable=protected-access
def _(executor, opcode):
	executor.scope['_'] = executor.scope[opcode.name]


@Executor._addHandler(actl.opcodes.CALL_FUNCTION_STATIC)  # pylint: disable=protected-access
def _(executor, opcode):
	function = executor.scope[opcode.function]
	assert opcode.typeb == '('
	executor.scope[opcode.dst] = function.call(*opcode.args, **opcode.kwargs)


@Executor._addHandler(actl.opcodes.CALL_FUNCTION)  # pylint: disable=protected-access
def _(executor, opcode):
	function = executor.scope[opcode.function]
	assert opcode.typeb == '('
	args = (executor.scope[key] for key in opcode.args)
	kwargs = {key: executor.scope[key] for key in opcode.kwargs}
	executor.scope[opcode.dst] = function.call(*args, **kwargs)
