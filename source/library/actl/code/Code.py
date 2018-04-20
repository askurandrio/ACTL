
from .opcodes import AnyOpCode


class Code(AnyOpCode, list):
	pass


class Definition(Code):
	def __init__(self, elem):
		self.elem = elem
