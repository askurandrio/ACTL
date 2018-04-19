
import actl


class SExecutor:
	def __init__(self, code):
		self.__idx = 0
		self.code = code

	def link(self):
		while self.__idx != len(self.code):
			self.__tact()
			self.__idx += 1
		return 'next'

	def __tact(self):
		opcode = self.code[self.__idx]

		if actl.tokens.VARIABLE == opcode:
			self.code.scope[opcode]
		elif actl.opcodes.SET_VARIABLE == opcode:
			return f'{opcode.dst.name} = {opcode.source.name}'
		elif actl.opcodes.BUILD_STRING == opcode:
			return f'{opcode.dst.name} = "{opcode.string}"'
		elif actl.opcodes.BUILD_NUMBER == opcode:
			return f'{opcode.dst.name} = {opcode.number}'
		elif actl.opcodes.RETURN == opcode:
			return f'return {opcode.var.name}'
		elif actl.opcodes.CALL_OPERATOR == opcode:
			result = ''
			if opcode.dst is not None:
				result += f'{self.__tact(opcode.dst)} = '
			result += f'operator("{opcode.operator}")'
			result += f'({", ".join(map(self.__tact, opcode.args))})'
			return result
		elif actl.opcodes.SAVE_CODE == opcode:
			return f'SAVE_CODE({opcode.function.name})'
		elif actl.opcodes.CALL_FUNCTION == opcode:
			args = ', '.join(map(lambda var: var.name, opcode.args))
			if args and opcode.kwargs:
				args += ', '
			args += ', '.join(f'{key}={value}' for key, value in opcode.kwargs.items())
			close_brucket = actl.tokenizator.tokens.OPERATOR(actl.tokenizator.tokens.OPERATOR.brackets[opcode.typeb]).operator
			return f'{opcode.dst.name} = {opcode.function.name}{opcode.typeb}{args}{close_brucket}'
		else:
			return f'repr({opcode})'
		raise RuntimeError(f'This opcode not found: {opcode}')
		return 'next'
