
import actl


class SExecutor:
	def __init__(self, code):
		self.__idx = 0
		self.scope = code.scope
		self.code = code

	def link(self):
		while True:
			while self.__idx < len(self.code):
				self.tact(self.code[self.__idx])
				self.__idx += 1
			if self.scope['codes']:
				self.code, self.__idx = self.scope['codes'].pop(-1)
				self.__idx += 1
			else:
				break
		return 'next'

	def tact(self, opcode):
		if actl.tokens.VARIABLE == opcode:
			return self.scope[opcode]
		elif actl.opcodes.SET_VARIABLE == opcode:
			self.scope[opcode.dst] = self.scope[opcode.src]
		elif actl.opcodes.BUILD_STRING == opcode:
			self.scope[opcode.dst] = opcode.string
		elif actl.opcodes.BUILD_NUMBER == opcode:
			self.scope[opcode.dst] = opcode.number
		elif actl.opcodes.RETURN == opcode:
			self.scope['__return'] = opcode.var
			self.scope, label = self.scope['stack'].pop(-1)
			self.tact(actl.opcodes.JUMP(label=label))
		elif actl.opcodes.CALL_OPERATOR == opcode:
			function = eval(f'lambda a, b: a {opcode.operator} b')
			values = (self.scope[var] for var in opcode.args)
			self.scope[opcode.dst] = function(*values)
		elif actl.opcodes.CALL_FUNCTION == opcode:
			function = self.scope[opcode.function]
			if function == 'print':
				self.scope[opcode.dst] = print(*(self.scope[arg] for arg in opcode.args))
				return None
			call_scope = function.scope.make_child()
			for arg in opcode.args:
				call_scope[arg] = self.scope[arg]
			assert not opcode.kwargs
			self.scope['stack'].append((self.scope, self.__idx))
			self.scope = call_scope
			self.tact(actl.opcodes.JUMP(label=function.label))
		elif actl.Code == opcode:
			self.scope['codes'].append((self.code, self.__idx))
			self.code = opcode
			self.__idx = -1
		else:
			raise RuntimeError(f'This opcode not found: {opcode}')
