from actl import objects
from actl.syntax import SyntaxRule, Value, Token, Parsed
from actl.syntax.BufferRule import BufferRule
from actl.utils import asDecorator, executeSyncCoroutine
from std.base.rules import CodeBlock
from actl.utils import executeSyncCoroutine


While = executeSyncCoroutine(objects.class_.call('While', (objects.While,)))


@asDecorator(
	lambda rule: executeSyncCoroutine(While.setAttribute('__syntaxRule__', rule))
)
@SyntaxRule.wrap(Value(While), Token(' '), manualApply=True, useParser=True)
def _syntaxRule(parser, inp):
	inpRule = BufferRule(parser, inp)
	inpRule.pop(Value(While))
	inpRule.pop(Token(' '))
	condition = tuple(inpRule.pop(Parsed(Token(':'))))
	inpRule.pop(Token(':'))
	code = CodeBlock(parser, inp).parse()
	while_ = executeSyncCoroutine(While.call(condition, code))
	inp.insert(0, [while_])
