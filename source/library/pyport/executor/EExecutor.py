
from actl import Code


class EExecutor:
	transform = property(lambda self: self.execute)

	def __init__(self, code):
		self.code = code

	def execute(self):
		for opcode in self.code:
			pass
