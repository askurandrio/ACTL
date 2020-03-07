from actl.Buffer import Buffer
from actl.objects.BuildClass import BuildClass
from actl.opcodes import CALL_FUNCTION_STATIC, RETURN
from actl.syntax import SyntaxRule, Value, Token, VARIABLE, IsInstance


Function = BuildClass('Function')


@Function.addMethodToClass('__call__')
def _(cls, name, signature, body):
	self = cls.getAttr('__super__').getAttr('__call__').call()

	self.setAttr('name', name)
	self.setAttr('signature', signature)
	if RETURN != body[-1]:
		body += (
			RETURN('None'),
		)
	self.setAttr('body', body)

	return self


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
	inp.pop()
	inp.pop()
	name = inp.pop().name
	inp.pop()
	inp.pop()
	inp.pop()
	inp.pop()
	body = tuple(parser.rules.find('UseCodeBlock').func.popCodeBlock(parser, inp))

	opcode = CALL_FUNCTION_STATIC(dst=name, function=Function.call, args=(name, (), body))
	inp.set_(Buffer.of(opcode) + inp)
