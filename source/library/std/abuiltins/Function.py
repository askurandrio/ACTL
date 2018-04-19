
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
		result += self.signature.typeb.mirror.operator
		return result

	def __repr__(self):
		return f'Function({self.name}, {self.signature}, {self.code})'


@actl.Project.this.add_syntax(actl.syntax.Value(Function),
										actl.syntax.Maybe(actl.tokenizer.tokens.VARIABLE),
										actl.syntax.Range((actl.tokenizer.tokens.OPERATOR('('),),
															lambda op: (op.mirror,)),
										args=('code', 'matched_code'))
def _(code, matched_code):
	matched_code = list(matched_code)

	function = matched_code.pop(0)
	assert Function == code.scope[function]

	if actl.tokenizer.tokens.VARIABLE == matched_code[0]:
		function_name = matched_code.pop(0)
	else:
		function_name = actl.tokenizer.tokens.VARIABLE.get_temp()

	function_typeb = matched_code[0]
	assert actl.tokenizer.tokens.OPERATOR('(') == matched_code.pop(0)
	assert actl.tokenizer.tokens.OPERATOR(')') == matched_code.pop(-1)

	function_args = []
	for opcode in matched_code:
		if actl.tokenizer.tokens.VARIABLE == opcode:
			function_args.append(opcode)
		elif actl.tokenizer.tokens.OPERATOR(',') == opcode:
			pass
		else:
			raise RuntimeError(opcode)

	definition = code.create_definition()
	definition.append(actl.code.opcodes.BUILD_STRING(out=actl.tokenizer.tokens.VARIABLE.get_temp(),
																	 string='create'))
	definition.append(actl.code.opcodes.CALL_OPERATOR(out=actl.tokenizer.tokens.VARIABLE.get_temp(),
																	  operator='.',
																	  args=[function, definition[0].out]))
	definition.append(actl.code.opcodes.CALL_FUNCTION(out=function_name,
																	  function=definition[1].out,
																	  typeb='(',
																	  args=[],
																	  kwargs={'typeb': function_typeb,
																				 'args': function_args}))
	return definition, function_name
