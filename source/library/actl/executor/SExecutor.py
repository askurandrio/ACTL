
from ..code.opcodes import opcodes


class SExecutor:
	def __init__(self, buff):
		self.scope = {}
		self.buff = buff

	def exec(self):
		for opcode in self.buff:
			if opcodes.SET_VARIABLE == opcode:
				self.scope[opcode.out.name] = self.scope[opcode.src.name]
			else:
				raise RuntimeError(f'This opcode not found: {opcode}')

