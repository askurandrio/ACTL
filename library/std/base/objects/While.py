from actl import objects
from actl.syntax import SyntaxRule, Value, Token, Parsed
from actl.syntax.BufferRule import BufferRule
from actl.utils import asDecorator
from std.base.rules import CodeBlock


While = objects.makeClass('While', (objects.While,))


@asDecorator(lambda rule: While.setAttribute('__syntaxRule__', rule))
@SyntaxRule.wrap(
	Value(While),
	Token(' '),
	manualApply=True,
	useParser=True
)
def _syntaxRule(parser, inp):
	inpRule = BufferRule(parser, inp)
	inpRule.pop(Value(While))
	inpRule.pop(Token(' '))
	condition = tuple(inpRule.pop(Parsed(Token(':'))))
	inpRule.pop(Token(':'))
	code = CodeBlock(parser, inp).parse()
	inp.insert(0, [While.call(condition, code)])
