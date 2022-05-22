from actl.objects import (
	makeClass,
	class_ as actlClass,
	Function as actlFunction,
	Signature,
	executeSyncCoroutine,
	NativeFunction,
)
from actl.opcodes import VARIABLE, RETURN
from actl.opcodes.opcodes import CALL_FUNCTION_STATIC
from actl.syntax import SyntaxRule, Value, Token, IsInstance, Maybe, Parsed
from actl import asDecorator
from actl.syntax.BufferRule import BufferRule
from std.base.rules import CodeBlock
from std.base.executor.utils import bindExecutor
from std.base.objects.function import Function


class_ = makeClass('class_', (actlClass,))


@asDecorator(lambda rule: class_.setAttribute('__syntaxRule__', rule))
@SyntaxRule.wrap(
	Value(class_),
	Token(' '),
	IsInstance(VARIABLE),
	Maybe(Token('('), IsInstance(VARIABLE), Token(')')),
	useParser=True,
	manualApply=True,
)
def _parseClass(parser, inp):
	inpRule = BufferRule(parser, inp)
	inpRule.pop(Value(class_), Token(' '))
	className = inpRule.pop(IsInstance(VARIABLE)).one().name

	parents = []
	if inpRule.startsWith(Token('(')):
		inpRule.pop(Token('('))
		parentName = inpRule.pop(Parsed(Token(')'))).one().name
		parents.append(parser.scope[parentName])
		inpRule.pop(Token(')'))

	inpRule.pop(Token(':'))
	body = CodeBlock(parser, inp).parse()
	makeClassOpcode = CALL_FUNCTION_STATIC(
		className, buildClass.call, staticArgs=(className, tuple(parents), body)
	)
	inp.insert(0, [makeClassOpcode])


@NativeFunction
async def buildClass(name, parents, body):
	cls = makeClass(name, parents)
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

		if actlFunction.isinstance_(value):
			self_[key] = value
			continue

		if executeSyncCoroutine(value.hasAttribute('__get__')):
			self_[key] = value
			continue

		cls.setAttribute(key, value)

	return cls
