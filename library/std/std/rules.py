from actl.syntax import Token, Parsed, Or, BufferRule, SyntaxRules
from actl.opcodes import CALL_FUNCTION_STATIC, GET_ATTRIBUTE, CALL_FUNCTION
from std.base.rules import RULES as stdRULES


RULES = SyntaxRules(stdRULES)


@RULES.add(Token('['), manualApply=True, useParser=True)
def _parseVector(parser, inp):
	inpRule = BufferRule(parser, inp)
	inpRule.pop(Token('['))
	dst = parser.makeTmpVar()
	parser.define(CALL_FUNCTION_STATIC(dst=dst.name, function=parser.scope['Vector'].call, args=[]))

	if not inpRule.startsWith(Token(']')):
		appendVarName = parser.makeTmpVar().name
		parser.define(
			GET_ATTRIBUTE(appendVarName, dst.name, 'append')
		)
		appendResultVarName = parser.makeTmpVar().name

		while not inpRule.startsWith(Token(']')):
			elementCode = inpRule.pop(Parsed(Or([Token(']')], [Token(',')])))
			elementVarName = elementCode.pop(-1).name
			parser.define(
				*elementCode,
				CALL_FUNCTION(appendResultVarName, appendVarName, args=[elementVarName])
			)

	inpRule.pop(Token(']'))
	inp.insert(0, [dst])
