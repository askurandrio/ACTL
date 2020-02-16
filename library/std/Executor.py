
import actl
from actl.objects import While, Object, Bool
from actl.objects.AToPy import AToPy


_HANDLERS = {}


class Executor:

	def __init__(self, code, scope):
		self.scope = scope

		self.execute(code)

	def execute(self, code):
		for opcode in code:
			handler = _HANDLERS[type(opcode)]
			handler(self, opcode)


def _addHandler(opcode):
	def decorator(handler):
		_HANDLERS[opcode] = handler
	return decorator


@_addHandler(type(Object))
def _(executor, opcode):
	assert opcode.getAttr('__class__').equal(While)

	def condition():
		executor.execute(opcode.getAttr('conditionFrame'))
		res = executor.scope['_']
		res = Bool.call(res)
		return AToPy(res)

	while condition():
		executor.execute(opcode.getAttr('code'))


@_addHandler(actl.opcodes.VARIABLE)
def _(executor, opcode):
	executor.scope['_'] = executor.scope[opcode.name]


@_addHandler(actl.opcodes.SET_VARIABLE)
def _(executor, opcode):
	executor.scope[opcode.dst] = executor.scope[opcode.src]


@_addHandler(actl.opcodes.CALL_FUNCTION_STATIC)
def _(executor, opcode):
	function = executor.scope[opcode.function]
	assert opcode.typeb == '('
	executor.scope[opcode.dst] = function.call(*opcode.args, **opcode.kwargs)


@_addHandler(actl.opcodes.CALL_FUNCTION)
def _(executor, opcode):
	function = executor.scope[opcode.function]
	assert opcode.typeb == '('
	args = (executor.scope[key] for key in opcode.args)
	kwargs = {key: executor.scope[key] for key in opcode.kwargs}
	executor.scope[opcode.dst] = function.call(*args, **kwargs)
