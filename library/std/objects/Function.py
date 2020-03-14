from actl import objects, Buffer
from actl.opcodes import CALL_FUNCTION_STATIC
from actl.syntax import SyntaxRule, Value, Token, VARIABLE, IsInstance, BufferRule

Function = objects.BuildClass('Function', objects.Function)


@Function.setAttr('__syntaxRule__')
@SyntaxRule.wrap(
	Value(Function),
	Token(' '),
	IsInstance(VARIABLE),
	Token('('),
	useParser=True,
	manualApply=True
)
def _(parser, inp):
	inpRule = BufferRule(parser, inp)
	inpRule.pop(Value(Function), Token(' '))
	name = inpRule.pop(IsInstance(VARIABLE)).one().name
	inpRule.pop(Token('('), Token(')'), Token(':'))
	body = tuple(parser.rules.find('UseCodeBlock').func.popCodeBlock(parser, inp))

	opcode = CALL_FUNCTION_STATIC(dst=name, function=Function.call, args=(name, (), body))
	inp.set_(Buffer.of(opcode) + inp)
