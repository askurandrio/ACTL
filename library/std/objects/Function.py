from itertools import zip_longest
from actl import objects
from actl.Result import Result
from actl.opcodes import VARIABLE, RETURN
from actl.syntax import SyntaxRule, Value, Token, IsInstance, BufferRule, Maybe
from actl import asDecorator
from std.rules import CodeBlock


Function = objects.makeClass('Function', (objects.Function,))
_default = object()


@objects.addMethod(Function, '__call__')
def _Function__call(self, *args):
	callScope = self.getAttribute.obj('scope').obj
	signature = self.getAttribute.obj('signature').obj
	argNames = signature.getAttribute.obj('args').obj
	body = self.getAttribute.obj('body').obj

	@Result.fromExecute
	def result(executor):
		executor.scope, prevScope = callScope.child(), executor.scope
		for argName, argValue in zip_longest(argNames, args, fillvalue=_default):
			assert argName is not _default, \
					f'argName is default, argValue is {argValue}'
			assert argValue is not _default, \
					f'argValue is default, argName is {argName}'
			executor.scope[argName] = argValue

		try:
			yield from body
		except GeneratorExit:
			executor.scope = prevScope

	return result


@asDecorator(lambda rule: Function.setAttribute('__syntaxRule__', rule))
@SyntaxRule.wrap(
	Value(Function),
	Token(' '),
	IsInstance(VARIABLE),
	Token('('),
	useParser=True,
	manualApply=True
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
		self._inp.insert(0, [Function.call.obj(name, signature, body, None).obj])

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
		signature = objects.Signature.call.obj(args).obj
		return signature

	def _parseBody(self):
		self._inpRule.pop(Token(':'))
		body = CodeBlock(self._parser, self._inp).parse()
		return (
			*body,
			RETURN('None')
		)
