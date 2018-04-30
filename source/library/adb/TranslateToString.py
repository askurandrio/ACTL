
from actl.tokenizer import tokens
from actl.code import Code, opcodes


class TranslateToString:
	def __init__(self, code, out_file):
		self.__out_file = out_file
		self.__code = code

	def link(self):		
		self.__out_file.write(''.join(self.__translate(self.__code)))
		return 'next'

	def exec(self):
		print(''.join(self.__translate(self.__code)))

	def __translate(self, code):
		from std.abuiltins import abuiltins

		ftype = abuiltins[tokens.VARIABLE('def')]

		for opcode in code:
			if Code == opcode:
				yield f'{type(opcode).__name__}:\n'
				for repr_opcode in self.__translate(opcode):
					yield '   ' + repr_opcode
			elif ftype == opcode:
				yield f'{opcode.to_string()}:\n'
				for repr_opcode in self.__translate(opcode.code):
					yield '   ' + repr_opcode
			else:
				yield self.__tact(opcode) + '\n'

	def __tact(self, opcode):
		if tokens.VARIABLE == opcode:
			return opcode.name
		elif opcodes.SET_VARIABLE == opcode:
			return f'{self.__tact(opcode.dst)} = {self.__tact(opcode.src)}'
		elif opcodes.BUILD_STRING == opcode:
			return f'{self.__tact(opcode.dst)} = "{opcode.string}"'
		elif opcodes.BUILD_NUMBER == opcode:
			return f'{self.__tact(opcode.dst)} = {opcode.number}'
		elif opcodes.RETURN == opcode:
			return f'return {opcode.var.name}'
		elif opcodes.CALL_OPERATOR == opcode:
			result = ''
			if opcode.dst is not None:
				result += f'{self.__tact(opcode.dst)} = '
			result += f'operator("{opcode.operator}")'
			result += f'({", ".join(map(self.__tact, opcode.args))})'
			return result
		elif opcodes.SAVE_CODE == opcode:
			return f'SAVE_CODE({opcode.function.name})'
		elif opcodes.CALL_FUNCTION == opcode:
			args = ', '.join(map(lambda var: var.name, opcode.args))
			if args and opcode.kwargs:
				args += ', '
			args += ', '.join(f'{key}={value}' for key, value in opcode.kwargs.items())
			close_brucket = tokens.OPERATOR(opcode.typeb).get_mirror().operator
			return f'{opcode.dst.name} = {opcode.function.name}{opcode.typeb}{args}{close_brucket}'
		elif tokens.OPERATOR('line_end') == opcode:
			return 'line_end'
		else:
			return f'repr({opcode})'
		raise RuntimeError(f'This opcode not found: {opcode}')
