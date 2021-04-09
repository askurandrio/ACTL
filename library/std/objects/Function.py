from actl import objects
from actl.opcodes import SET_VARIABLE, VARIABLE, RETURN
from actl.syntax import SyntaxRule, Value, Token, IsInstance, BufferRule
from actl import asDecorator


Function = objects.makeClass('Function', (objects.Function,))


@objects.addMethod(Function, '__useCodeBlock__')
def _useCodeBlock(self, body):
	if RETURN != body[-1]:
		body = (
			*body,
			RETURN('None'),
		)

	self.setAttribute('body', body)
	return []


@asDecorator(lambda rule: Function.setAttribute('__syntaxRule__', rule))
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
	nameVar = inpRule.pop(IsInstance(VARIABLE)).one()
	inpRule.pop(Token('('))
	signature = _parseSignature(inpRule)
	inpRule.pop(Token(')'))
	function = Function.call(nameVar.name, signature, None)
	parser.define(
		SET_VARIABLE(nameVar.name, src=None, srcStatic=function)
	)
	inp.insert(0, [function])


def _parseSignature(inpRule):
	args = []
	inpRule.parseUntil(Token(')'))

	while inpRule.startsWith(IsInstance(VARIABLE)):
		args.append(inpRule.pop(IsInstance(VARIABLE)).one().name)
		if inpRule.startsWith(Token(',')):
			inpRule.pop(Token(','))

	signature = objects.Signature.call(args)
	return signature
