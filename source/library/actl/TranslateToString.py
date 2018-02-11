
from actl.parser import tokens
from actl.code import Code, opcodes


class TranslateToString:
	def __init__(self):
		self.string = ''

	def translate(self, code):
		from actl.project.Project import Project

		self.string = ''.join(self.__translate(code))
		open(Project.this.get('translator', 'out'), 'w').write(self.string)

	def __translate(self, code):
		from pyport.executor.abuiltins import abuiltins

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
			return f'{opcode.out.name} = {opcode.source.name}'
		elif opcodes.BUILD_STRING == opcode:
			return f'{opcode.out.name} = "{opcode.string}"'
		elif opcodes.BUILD_NUMBER == opcode:
			return f'{opcode.out.name} = {opcode.number}'
		elif opcodes.RETURN == opcode:
			return f'return {opcode.var.name}'
		elif opcodes.CALL_FUNCTION == opcode:
			args = ', '.join(map(lambda var: var.name, opcode.args))
			if args and opcode.kwargs:
				args += ', '
			args += ', '.join(opcode.kwargs)
			close_brucket = tokens.OPERATOR(tokens.OPERATOR.brackets[opcode.typeb]).operator
			return f'{opcode.out.name} = {opcode.function.name}{opcode.typeb}{args}{close_brucket}'
		else:
			return f'repr({opcode})'
		raise RuntimeError(f'This opcode not found: {opcode}')
