
import actl


class Function:
	def __init__(self, name, signature, code):
		self.name = name
		self.signature = signature
		self.code = code

	def set_code(self, code):
		self.code = code

	def to_string(self):
		result = ''
		result += self.signature.return_type + ' '
		result += 'def ' + self.name.name
		result += self.signature.typeb.operator
		result += ', '.join(arg.name for arg in self.signature.args)
		result += self.signature.typeb.get_mirror().operator
		return result

	def __repr__(self):
		return f'Function({self.name}, {self.signature}, {self.code})'


@actl.Project.this.add_syntax(actl.syntax.Value(Function),
										actl.syntax.Maybe(actl.tokens.VARIABLE),
										actl.syntax.Range((actl.tokens.OPERATOR('('),),
																lambda op: (op.get_mirror(),)),
										args=('buff',))
def _(buff):
	function = buff.pop()

	if actl.tokens.VARIABLE == buff[0]:
		dst = buff.pop()
	else:
		dst = actl.tokens.VARIABLE.get_temp()

	close_bracket_op = buff[0].get_mirror()
	function_typeb = buff.pop().operator

	function_args = []
	while True:
		if actl.tokens.VARIABLE == buff[0]:
			function_args.append(buff.pop())
			if actl.tokens.OPERATOR(',') == buff[0]:
				buff.pop()
		elif close_bracket_op == buff[0]:
			buff.pop()
			break
		else:
			raise RuntimeError(buff[0])

	yield actl.Definition(actl.opcodes.CALL_FUNCTION(
		dst=dst,
		function=function.name,
		typeb='(',
		args=[],
		kwargs={'typeb': function_typeb, 'args': function_args}
	))
	yield function
