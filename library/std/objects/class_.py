from actl.objects import makeClass, class_ as actlClass, addMethodToClass
from actl.opcodes import VARIABLE
from actl.syntax import SyntaxRule, Value, Token, IsInstance
from actl import asDecorator
from actl.syntax.BufferRule import BufferRule
from std.rules import CodeBlock


class_ = makeClass('class_', (actlClass,))


@addMethodToClass(class_, '__call__')
def _class_call(_, name, scope):
	self = makeClass(name)

	for key, value in scope.items():
		self.setAttribute(key, value)

	return self


@asDecorator(lambda rule: class_.setAttribute('__syntaxRule__', rule))
@SyntaxRule.wrap(
	Value(class_), Token(' '), IsInstance(VARIABLE),
	useParser=True,
	manualApply=True
)
def _parseClass(parser, inp):
	inpRule = BufferRule(parser, inp)
	inpRule.pop(Value(class_), Token(' '))
	clsName = inpRule.pop(IsInstance(VARIABLE)).one().name
	inpRule.pop(Token(':'))
	body = CodeBlock(parser, inp).parse()
	cls = class_.call(clsName, {'body': body})
	inp.insert(0, [cls])
