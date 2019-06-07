
import actl


_HANDLERS = {}


def Executor(code, scope):
	for opcode in code:
		handler = _HANDLERS[type(opcode)]
		handler(scope, opcode)


def _add_handler(opcode):
	def decorator(handler):
		_HANDLERS[opcode] = handler
	return decorator


@_add_handler(type(actl.opcodes.END_LINE))
def _(_, _1):
	pass


@_add_handler(actl.opcodes.VARIABLE)
def _(scope, opcode):
	scope[opcode]


@_add_handler(actl.opcodes.BUILD_STRING)
def _(scope, opcode):
	stringCls = scope[actl.tokens.VARIABLE('String')]
	scope[opcode.dst] = stringCls.fromPy(opcode.string)


@_add_handler(actl.opcodes.BUILD_NUMBER)
def _(scope, opcode):
	numberCls = scope[actl.tokens.VARIABLE('Number')]
	scope[opcode.dst] = numberCls.fromPy(opcode.number)


@_add_handler(actl.opcodes.CALL_FUNCTION)
def _(scope, opcode):
	function = scope[opcode.function]
	assert opcode.typeb == '('
	assert not opcode.args
	assert not opcode.kwargs
	scope[opcode.dst] = function.call()
