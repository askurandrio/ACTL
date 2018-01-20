
from ..code import Code
from ..code.opcodes import opcodes

class CTuple(object):
	def __init__(self, args, kwargs):
		self.args = args
		self.kwargs = kwargs


class	Scope:
	def __init__(self, parent=None):
		self.head = {}
		self.parent = {} if parent is None else parent

	def get_child(self):
		return type(self)(self)

	def __getitem__(self, key):
		try:
			return self.head[key]
		except KeyError:
			return self.parent[key]

	def __setitem__(self, key, value):
		self.head[key] = value


class SExecutor:
	def __init__(self, buff):
		self.scope = Scope()
		self.buff = buff

	def exec(self):
		self.__exec(self.buff)

	def __exec(self, code):
		for opcode in code:
			self.__tact(opcode)

	def __tact(self, opcode):
		if Code == opcode:
			self.__exec(opcode)
		elif opcodes.SET_VARIABLE == opcode:
			self.scope[opcode.out.name] = self.scope[opcode.src.name]
		elif opcodes.BUILD_CTUPLE == opcode:
			self.scope[opcode.out.name] = CTuple(opcode.args, opcode.kwargs)
		elif opcodes.BUILD_STRING == opcode:
			self.scope[opcode.out.name] = str(opcode.string)
		elif opcodes.CALL_FUNCTION == opcode:
			function = self.scope[opcode.function.name]
			ctuple = self.scope[opcode.ctuple.name]
			self.scope = self.scope.get_child()
			assert not ctuple.args
			for key, value in ctuple.kwargs:
				self.scope[key] = value
		else:
			raise RuntimeError(f'This opcode not found: {opcode}')
			
