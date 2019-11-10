
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


@_addHandler(actl.opcodes.BUILD_STRING)
def _(scope, opcode):
	stringCls = scope[actl.opcodes.VARIABLE('String').name]
	scope[opcode.dst.name] = stringCls.fromPy(opcode.string)


@_addHandler(actl.opcodes.BUILD_NUMBER)
def _(scope, opcode):
	numberCls = scope[actl.opcodes.VARIABLE('Number').name]
	scope[opcode.dst.name] = numberCls.fromPy(opcode.number)


@_addHandler(actl.opcodes.CALL_FUNCTION)
def _(scope, opcode):
	function = scope[opcode.function]
	assert opcode.typeb == '('
	args = (scope[key] for key in opcode.args)
	kwargs = {key:scope[key] for key in opcode.kwargs}
	scope[opcode.dst] = function.call(*args, **kwargs)
