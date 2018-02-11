
import actl


FIND_BRACKETS = actl.syntax.Range( \
						 (actl.syntax.Or( \
							 *((actl.parser.tokens.OPERATOR(bracket),) \
								 for bracket in actl.parser.tokens.OPERATOR.brackets)),),
						 lambda open_bracket: (open_bracket.mirror,))

class Signature:
	def __init__(self, return_type, typeb, args, kwargs):
		self.return_type = return_type
		self.typeb = typeb
		self.args = args
		self.kwargs = kwargs

	def __repr__(self):
		return f'Signature({self.return_type}, {self.typeb}, {self.args}, {self.kwargs})'


class Function(actl.code.opcodes.AnyOpCode):
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
										actl.syntax.ToSpecific(actl.parser.tokens.OPERATOR(':')),
										args=('code', 'idx_start', 'idx_end'))
def _(code, idx_start, idx_end):
	subcode = code[idx_start:idx_end]
	assert Function == subcode.scope[subcode.pop(0)]
	rfind_brackets = FIND_BRACKETS.match(subcode, subcode.buff)
	if rfind_brackets and (rfind_brackets.idx_end == (len(subcode) - 2)):
		name = actl.parser.tokens.VARIABLE.get_temp()
		typeb, _ = subcode.pop(0), subcode.pop(-2)
	else:
		rfind_brackets = FIND_BRACKETS.match(subcode, subcode.buff[1:])
		if rfind_brackets and (rfind_brackets.idx_end == (len(subcode) - 2)):
			name = subcode.pop(0)
			typeb, _ = subcode.pop(0), subcode.pop(-2)
		else:
			name = actl.parser.tokens.VARIABLE.get_temp()
			typeb = actl.parser.tokens.OPERATOR('(')
	signature = Signature('object', typeb, [], {})
	while len(subcode) > 1:
		signature.args.append(subcode.pop(0))
		if len(subcode) > 1:
			assert subcode.pop(0) == actl.parser.tokens.OPERATOR(',')
	assert tuple(subcode) == (actl.parser.tokens.OPERATOR(':'),)

	out = actl.parser.tokens.VARIABLE.get_temp()
	function = Function(name, signature, (actl.code.opcodes.PASS,))
	definition = code.create_definition()
	definition.append(function)
	definition.append(actl.code.opcodes.SET_VARIABLE(out=out, source=function.name))
	return definition, \
			 out, \
			 actl.code.opcodes.BUILD_CODE(function.set_code)
