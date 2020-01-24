
import actl


_HANDLERS = {}


def Executor(code, scope):
	for opcode in code:
		handler = _HANDLERS[type(opcode)]
		handler(scope, opcode)


def _addHandler(opcode):
	def decorator(handler):
		_HANDLERS[opcode] = handler
	return decorator


@_addHandler(type(actl.opcodes.END_LINE))
def _(_, _1):
	pass


@_addHandler(actl.opcodes.VARIABLE)
def _(scope, opcode):
	scope[opcode.name]


@_addHandler(actl.opcodes.CALL_FUNCTION_STATIC)
def _(scope, opcode):
	function = scope[opcode.function]
	assert opcode.typeb == '('
	scope[opcode.dst] = function.call(*opcode.args, **opcode.kwargs)


@_addHandler(actl.opcodes.CALL_FUNCTION)
def _(scope, opcode):
	function = scope[opcode.function]
	assert opcode.typeb == '('
	args = (scope[key] for key in opcode.args)
	kwargs = {key:scope[key] for key in opcode.kwargs}
	scope[opcode.dst] = function.call(*args, **kwargs)
