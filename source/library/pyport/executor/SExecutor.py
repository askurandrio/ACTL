
from actl import Code


class SExecutor:
	def __init__(self, code, scope):
		self.code = code
		self.scope = scope

	def execute(self):
		self.code.compile()
		print(self.code)
		self.__tact(self.code)
		while self.code.compile():
			print(self.code)
			self.__tact(opcode)

	def __tact(self, code):
		for opcode in code:
			pass
		pass