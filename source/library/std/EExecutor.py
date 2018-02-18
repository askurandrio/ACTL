
from actl import Code


class EExecutor:
	transform = property(lambda self: self.execute)

	def __init__(self, code):
		from std.abuiltins import abuiltins

		self.code = code
		self.code.scope.update(abuiltins)

	def execute(self):
		for opcode in self.code:
			pass
