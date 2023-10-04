from actl import objects, asDecorator
from actl.utils import executeSyncCoroutine
from actl.opcodes import VARIABLE, RETURN, CALL_FUNCTION_STATIC
from actl.syntax import SyntaxRule, Value, Token, IsInstance, BufferRule, Maybe
from std.base.rules import CodeBlock
from std.base.executor.utils import bindExecutor, CallFrame


Function = executeSyncCoroutine(objects.class_.call('Function', (objects.Function,)))
_default = object()


@Function.addMethod('__call__')
async def _Function__call(self, *args):
	callScope = objects.AToPy(await self.getAttribute('scope'))
	signature = await self.getAttribute('signature')
	argNames = await signature.getAttribute('args')
	body = await self.getAttribute('body')

	executor = await bindExecutor()
	executor.scope, prevScope = callScope.child(), executor.scope

	assert len(argNames) == len(args), f'len({argNames=}) != len({args=})'

	for argName, argValue in zip(argNames, args):
		executor.scope[argName] = argValue

	result = await CallFrame(body)
	executor.scope = prevScope

	return result


@asDecorator(
	lambda rule: executeSyncCoroutine(
		Function.setAttribute(
			'__syntaxRule__', executeSyncCoroutine(objects.PyToA.call(rule))
		)
	)
)
@SyntaxRule.wrap(
	Value(Function),
	Token(' '),
	IsInstance(VARIABLE),
	Token('('),
	useParser=True,
	manualApply=True,
)
class _ParseFunction:
	def __init__(self, parser, inp):
		self._parser = parser
		self._inp = inp
		self._inpRule = BufferRule(parser, inp)

	async def parse(self):
		await self._inpRule.pop(Value(Function), Token(' '))
		name = await self._parseName()
		signature = await self._parseSignature()
		if await self._inpRule.startsWith(Token(':')):
			body = await self._parseBody()
		else:
			body = None
		makeFunctionOpcode = CALL_FUNCTION_STATIC(
			name,
			Function.call,
			staticArgs=(name, signature, body),
			kwargs={'scope': '__scope__'},
		)
		self._inp.insert(0, [makeFunctionOpcode])

	async def _parseName(self):
		return (await self._inpRule.pop(IsInstance(VARIABLE))).one().name

	async def _parseSignature(self):
		args = []
		await self._inpRule.pop(Token('('))

		while not await self._inpRule.startsWith(Token(')')):
			self._inpRule.parseUntil(IsInstance(VARIABLE))
			argVar = (await self._inpRule.pop(IsInstance(VARIABLE))).one().name
			args.append(argVar)
			if await self._inpRule.startsWith(Token(',')):
				await self._inpRule.pop(Token(','), Maybe(Token(' ')))

		await self._inpRule.pop(Token(')'))
		signature = executeSyncCoroutine(objects.Signature.call(args))
		return signature

	async def _parseBody(self):
		await self._inpRule.pop(Token(':'))
		body = await CodeBlock(self._parser, self._inp).parse()

		if (not body) or (RETURN != body[-1]):
			body = (*body, RETURN('None'))

		return body
