from actl import objects
from actl.Buffer import Buffer
from actl.opcodes import CALL_FUNCTION_STATIC, VARIABLE
from actl.syntax import SyntaxRule, Value, Token, IsInstance, BufferRule
from std.rules import UseCodeBlock


Function = objects.makeClass('Function', (objects.Function,))


@SyntaxRule.wrap(
	Value(Function),
	Token(' '),
	IsInstance(VARIABLE),
	Token('('),
	useParser=True,
	manualApply=True
)
def _syntaxRule(parser, inp):
	inpRule = BufferRule(parser, inp)
	inpRule.pop(Value(Function), Token(' '))
	name = inpRule.pop(IsInstance(VARIABLE)).one().name
	inpRule.pop(Token('('))
	signature = _parseSignature(inpRule)
	inpRule.pop(Token(')'), Token(':'))
	body = Buffer(UseCodeBlock.popCodeBlock(parser, inp)).loadAll()

	opcode = CALL_FUNCTION_STATIC(dst=name, function=Function.call, args=(name, signature, body))

	return Buffer.of(opcode)


def _parseSignature(inpRule):
	args = []
	inpRule.parseUntil(Token(')'))

	while inpRule.startsWith(IsInstance(VARIABLE)):
		args.append(inpRule.pop(IsInstance(VARIABLE)).one().name)
		if inpRule.startsWith(Token(',')):
			inpRule.pop(Token(','))

	signature = objects.Signature.call(args)
	return signature


Function.setAttribute('__syntaxRule__', _syntaxRule)
