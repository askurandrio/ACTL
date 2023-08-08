from actl import objects
from actl.syntax import SyntaxRule, Value, Token, Parsed
from actl.syntax.BufferRule import BufferRule
from actl.utils import asDecorator, executeSyncCoroutine, loadCoroutine
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
	definition, condition = loadCoroutine(inpRule.pop(Parsed.until(Token(':'))))
	condition = (*definition, *condition)
	while_ = executeSyncCoroutine(While.call(condition, None))
	inp.insert(0, [while_])


@While.addMethod('__useCodeBlock__')
async def _While__useCodeBlock__(self, codeBlock):
	code = None

	async def parse():
		nonlocal codeBlock, code

		codeBlock = objects.AToPy(codeBlock)
		code = tuple(await codeBlock.parse())
		codeBlock.inp.insert(0, (self,))

	async def apply():
		await self.setAttribute('code', code)

	return await objects.PyToA.call((parse, apply))
