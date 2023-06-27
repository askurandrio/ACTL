from actl.objects import (
	class_ as actlClass,
	Function as actlFunction,
	Signature,
	NativeFunction,
)
from actl.opcodes import VARIABLE, RETURN
from actl.opcodes.opcodes import CALL_FUNCTION_STATIC
from actl.syntax import SyntaxRule, Value, Token, IsInstance, Maybe, ParsedOld
from actl import asDecorator, executeSyncCoroutine
from actl.syntax.BufferRule import BufferRule
from std.base.rules import CodeBlock
from std.base.executor.utils import bindExecutor
from std.base.objects.function import Function


class_ = executeSyncCoroutine(actlClass.call('class_', baseParent=actlClass))


@asDecorator(
	lambda rule: executeSyncCoroutine(class_.setAttribute('__syntaxRule__', rule))
)
@SyntaxRule.wrap(
	Value(class_),
	Token(' '),
	IsInstance(VARIABLE),
	Maybe(Token('('), IsInstance(VARIABLE), Token(')')),
	useParser=True,
	manualApply=True,
)
async def _parseClass(parser, inp):
	inpRule = BufferRule(parser, inp)
	await inpRule.pop(Value(class_), Token(' '))
	className = (await inpRule.pop(IsInstance(VARIABLE))).one().name

	parents = []
	if await inpRule.startsWith(Token('(')):
		await inpRule.pop(Token('('))
		parentName = (await inpRule.pop(ParsedOld(Token(')')))).one().name
		parents.append(parser.scope[parentName])
		await inpRule.pop(Token(')'))

	await inpRule.pop(Token(':'))
	body = await CodeBlock(parser, inp).parse()
	buildClassOpcode = CALL_FUNCTION_STATIC(
		className, buildClass.call, staticArgs=(className, tuple(parents), body)
	)
	inp.insert(0, [buildClassOpcode])


@NativeFunction
async def buildClass(name, parents, body):
	cls = executeSyncCoroutine(actlClass.call(name, parents))
	self_ = await cls.getAttribute('__self__')

	executor = await bindExecutor()
	builder = await Function.call(
		f'_build{name}',
		await Signature.call(['__class__', name]),
		[*body, RETURN('__scope__')],
		executor.scope,
	)
	scope = await builder.call(cls, cls)
	for key, value in scope.getDiff():
		if key in ['__class__', name]:
			continue

		if await actlFunction.isinstance_(value):
			self_[key] = value
			continue

		if executeSyncCoroutine(value.hasAttribute('__get__')):
			self_[key] = value
			continue

		await cls.setAttribute(key, value)

	return cls
