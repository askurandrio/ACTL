from actl.syntax import Token, Parsed, Or, BufferRule, SyntaxRules, IsInstance
from actl.opcodes import CALL_FUNCTION_STATIC, GET_ATTRIBUTE, CALL_FUNCTION, VARIABLE
from std.base.rules import RULES as stdRULES


RULES = SyntaxRules(stdRULES)


@RULES.add(IsInstance(VARIABLE), Token('['), manualApply=True, useParser=True)
def _parseSlice(parser, inp):
	inpRule = BufferRule(parser, inp)
	collectionVariable = inpRule.pop(IsInstance(VARIABLE)).one()
	inpRule.pop(Token('['))

	startDeclarationCode = inpRule.pop(Parsed(Token(':')))
	startVariable = startDeclarationCode.pop(-1)
	parser.define(*startDeclarationCode)
	inpRule.pop(Token(':]'))

	sliceVariable = parser.makeTmpVar()
	parser.define(CALL_FUNCTION_STATIC(dst=sliceVariable.name, function='Slice', args=[startVariable.name, 'None', 'None']))

	getItemMethodVariable = parser.makeTmpVar()
	parser.define(GET_ATTRIBUTE(getItemMethodVariable.name, collectionVariable.name, '__getItem__'))

	subCollectionVariable = parser.makeTmpVar()
	parser.define(
		CALL_FUNCTION(subCollectionVariable.name, getItemMethodVariable.name, args=[sliceVariable.name])
	)

	inp.insert(0, [subCollectionVariable])


@RULES.add(Token('['), manualApply=True, useParser=True)
def _parseVector(parser, inp):
	inpRule = BufferRule(parser, inp)
	inpRule.pop(Token('['))
	dst = parser.makeTmpVar()
	parser.define(CALL_FUNCTION_STATIC(dst=dst.name, function='Vector'))

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
