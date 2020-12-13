from actl import objects
from actl.Buffer import Buffer
from actl.opcodes import CALL_FUNCTION_STATIC, VARIABLE
from actl.syntax import SyntaxRule, Value, Token, IsInstance, BufferRule
from std.rules import UseCodeBlock

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
	body = tuple(UseCodeBlock.popCodeBlock(parser, inp))

	opcode = CALL_FUNCTION_STATIC(dst=name, function=Function.call, args=(name, (), body))

	return Buffer.of(opcode)
