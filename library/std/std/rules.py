from actl.syntax import *
from actl.opcodes import *
from actl.objects import NativeFunction, PyToA
from actl import executeSyncCoroutine
from std.base.executor import bindExecutor
from std.base.rules import RULES as stdRULES, parseSetVariable


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
	parser.define(
		CALL_FUNCTION_STATIC(
			dst=sliceVariable.name,
			function='Slice',
			args=[startVariable.name, 'None', 'None'],
		)
	)

	getItemMethodVariable = parser.makeTmpVar()
	parser.define(
		GET_ATTRIBUTE(
			getItemMethodVariable.name, collectionVariable.name, '__getItem__'
		)
	)

	subCollectionVariable = parser.makeTmpVar()
	parser.define(
		CALL_FUNCTION(
			subCollectionVariable.name,
			getItemMethodVariable.name,
			args=[sliceVariable.name],
		)
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
		parser.define(GET_ATTRIBUTE(appendVarName, dst.name, 'append'))
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


@NativeFunction
async def vector__of(*args):
	executor = await bindExecutor()
	Vector = executor.scope['Vector']
	vector = await Vector.call()
	append = await vector.getAttribute('append')
	for element in args:
		await append.call(element)

	return vector


def disableRules(rules, template):
	template = Template(*template)

	def match(parser, inp):
		with parser.rules.disable(*rules):

			return template(parser, inp)

	return match


@RULES.add(
	IsInstance(VARIABLE),
	Token(', '),
	IsInstance(VARIABLE),
	Many(
		Token(','),
		Maybe(Token(' ')),
		disableRules([parseSetVariable, '_parseConstVector'], [Parsed()]),
		IsInstance(VARIABLE),
		minMatches=0,
	),
	useParser=True,
)
def _parseConstVector(*inp, parser):
	args = [arg.name for arg in inp if VARIABLE == arg]
	dst = parser.makeTmpVar()

	parser.define(CALL_FUNCTION_STATIC(dst.name, vector__of.call, args=args))

	return [dst]


@CustomTemplate.create
def _setVariableDstIsUnpack(parser, buff):
	setVariableOpcode = buff.get()
	if SET_VARIABLE != setVariableOpcode:
		return None

	dst = setVariableOpcode.dst
	if not parser.makeTmpVar.isTmpVar(dst):
		return None

	dstDefinition = parser.definition.filter(
		lambda opcode: (CALL_FUNCTION_STATIC == opcode) and (opcode.dst == dst)
	)
	if not dstDefinition:
		return None

	dstDefinition = dstDefinition.one()
	if dstDefinition.function != vector__of.call:
		return None

	return [[buff.pop(), dstDefinition]]


@RULES.add(_setVariableDstIsUnpack, useParser=True)
def _parseSetWithUnpack(setVariableInfo, parser):
	setVariableOpcode, dstDefinition = setVariableInfo
	parser.definition = parser.definition.filter(lambda opcode: opcode != dstDefinition)

	with parser.makeTmpVar.onNestedScope():
		srcAsIter = parser.makeTmpVar().name
		srcIterNext = parser.makeTmpVar().name

	parser.define(
		CALL_FUNCTION(srcAsIter, 'Iter', args=[setVariableOpcode.src]),
		GET_ATTRIBUTE(srcIterNext, srcAsIter, 'next'),
	)

	for arg in dstDefinition.args:
		parser.define(CALL_FUNCTION(arg, srcIterNext))

	return ()


@CustomTemplate.createToken
def _isDigit(_, token):
	return isinstance(token, str) and token.isdigit()


@RULES.add(
	Maybe(Token('-')), Many(_isDigit), Maybe(Token('.'), Many(_isDigit)), useParser=True
)
def _parseNumber(*args, parser=None):
	number = ''.join(args)
	aProxy = executeSyncCoroutine(PyToA.call(number))
	dst = parser.makeTmpVar()
	parser.define(
		CALL_FUNCTION_STATIC(dst=dst.name, function='Number', staticArgs=[aProxy])
	)
	return [dst]
