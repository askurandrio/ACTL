
from actl import Code
from actl.code.opcodes import opcodes
from actl.parser.opcodes import OPERATOR


class TranslateToString:
	def __init__(self):
		self.string = ''

	def translate(self, code):
		self.string = ''.join(self.__translate(code))

	def __translate(self, code):
		for opcode in code:
			if Code == opcode:
				yield 'code:\n'
				for repr_opcode in self.__translate(opcode):
					yield '   ' + repr_opcode
			else:
				yield self.__tact(opcode) + '\n'

	def __tact(self, opcode):
		if opcodes.VARIABLE == opcode:
			return opcode.name
		elif opcodes.SET_VARIABLE == opcode:
			return f'{opcode.out.name} = {opcode.source.name}'
		elif opcodes.BUILD_STRING == opcode:
			return f'{opcode.out.name} = "{opcode.string}"'
		elif opcodes.BUILD_NUMBER == opcode:
			return f'{opcode.out.name} = {opcode.number}'
		elif opcodes.CALL_FUNCTION == opcode:
			args = ', '.join(map(lambda var: var.name, opcode.args))
			if args and opcode.kwargs:
				args += ', '
			args += ', '.join(opcode.kwargs)
			close_brucket = OPERATOR(OPERATOR.brackets[opcode.type]).operator
			return f'{opcode.out.name} = {opcode.function.name}{opcode.type}{args}{close_brucket}'
		else:
			return repr(opcode)
		raise RuntimeError(f'This opcode not found: {opcode}')
