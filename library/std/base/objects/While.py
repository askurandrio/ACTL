from actl import objects
from actl.syntax import SyntaxRule, Value, Token, ParsedOld
from actl.syntax.BufferRule import BufferRule
from actl.utils import asDecorator, executeSyncCoroutine
from std.base.rules import CodeBlock


While = executeSyncCoroutine(objects.class_.call('While', (objects.While,)))


@asDecorator(
	lambda rule: executeSyncCoroutine(While.setAttribute('__syntaxRule__', rule))
)
@SyntaxRule.wrap(Value(While), Token(' '), manualApply=True, useParser=True)
async def _syntaxRule(parser, inp):
	inpRule = BufferRule(parser, inp)
	await inpRule.pop(Value(While))
	await inpRule.pop(Token(' '))
	condition = tuple(await inpRule.pop(ParsedOld(Token(':'))))
	await inpRule.pop(Token(':'))
	code = await CodeBlock(parser, inp).parse()
	while_ = executeSyncCoroutine(While.call(condition, code))
	inp.insert(0, [while_])
