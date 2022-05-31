from itertools import zip_longest
from actl import objects, asDecorator
from actl.utils import executeSyncCoroutine
from actl.opcodes import VARIABLE, RETURN, CALL_FUNCTION_STATIC
from actl.syntax import SyntaxRule, Value, Token, IsInstance, BufferRule, Maybe
from std.base.rules import CodeBlock
from std.base.executor.utils import bindExecutor, CallFrame
from actl.utils import executeSyncCoroutine


Function = objects.makeClass('Function', (objects.Function,))
_default = object()


@objects.addMethod(Function, '__call__')
async def _Function__call(self, *args):
	callScope = await self.getAttribute('scope')
	signature = await self.getAttribute('signature')
	argNames = await signature.getAttribute('args')
	body = await self.getAttribute('body')

	executor = await bindExecutor()
	executor.scope, prevScope = callScope.child(), executor.scope

	for argName, argValue in zip_longest(argNames, args, fillvalue=_default):
		assert argName is not _default, f'argName is default, argValue is {argValue}'
		assert argValue is not _default, f'argValue is default, argName is {argName}'
		executor.scope[argName] = argValue

	result = await CallFrame(body)
	executor.scope = prevScope

	return result


@asDecorator(
	lambda rule: executeSyncCoroutine(Function.setAttribute('__syntaxRule__', rule))
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

	def parse(self):
		self._inpRule.pop(Value(Function), Token(' '))
		name = self._parseName()
		signature = self._parseSignature()
		if self._inpRule.startsWith(Token(':')):
			body = self._parseBody()
		else:
			body = None
		makeFunctionOpcode = CALL_FUNCTION_STATIC(
			name,
			Function.call,
			staticArgs=(name, signature, body),
			kwargs={'scope': '__scope__'},
		)
		self._inp.insert(0, [makeFunctionOpcode])

	def _parseName(self):
		return self._inpRule.pop(IsInstance(VARIABLE)).one().name

	def _parseSignature(self):
		args = []
		self._inpRule.pop(Token('('))

		while not self._inpRule.startsWith(Token(')')):
			self._inpRule.parseUntil(IsInstance(VARIABLE))
			argVar = self._inpRule.pop(IsInstance(VARIABLE)).one().name
			args.append(argVar)
			if self._inpRule.startsWith(Token(',')):
				self._inpRule.pop(Token(','), Maybe(Token(' ')))

		self._inpRule.pop(Token(')'))
		signature = executeSyncCoroutine(objects.Signature.call(args))
		return signature

	def _parseBody(self):
		self._inpRule.pop(Token(':'))
		body = CodeBlock(self._parser, self._inp).parse()

		if (not body) or (RETURN != body[-1]):
			body = (*body, RETURN('None'))

		return body
