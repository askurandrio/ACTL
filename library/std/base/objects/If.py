from actl import objects
from actl.Buffer import Buffer
from actl.syntax import SyntaxRule, Value, Token, Parsed, Or, BufferRule
from actl.utils import asDecorator, executeSyncCoroutine
from std.base.rules import CodeBlock


If = executeSyncCoroutine(objects.class_.call('If', (objects.If,)))


@asDecorator(lambda rule: executeSyncCoroutine(If.setAttribute('__syntaxRule__', rule)))
@SyntaxRule.wrap(Value(If), Token(' '), useParser=True, manualApply=True)
class IfSyntax:
	_INLINE_IF_END = Or(
		(Token(' '), Value(objects.elif_)),
		(Value(objects.elif_),),
		(Token(' '), Value(objects.else_)),
		(Value(objects.else_),),
		(Token(' '), Token('\n')),
		(Token('\n'),),
	)
	_ELIF_OR_ELSE_OR_ENDLINE = Or(
		(Value(objects.elif_),), (Value(objects.else_),), (Token('\n'),)
	)

	def __init__(self, parser, inp):
		self._parser = parser
		self._inp = inp
		self._inpRule = BufferRule(self._parser, self._inp)

	async def parse(self):
		await self._inpRule.pop(Value(If), Token(' '))
		self._firstConditionFrame = tuple(await self._inpRule.pop(Parsed(Token(':'))))
		await self._inpRule.pop(Token(':'))
		if await CodeBlock(self._parser, self._inp).isFullCodeBlock():
			conditions, elseCode = await self._getFromFullCodeBlock()
		else:
			conditions, elseCode = await self._getFromInlineCodeBlock()
		if_ = executeSyncCoroutine(If.call(*conditions, elseCode=elseCode))
		self._inp.insert(0, [if_])

	async def _getFromFullCodeBlock(self):
		async def popCodeBlock():
			code = Buffer(await CodeBlock(self._parser, self._inp).parseFullCodeBlock())
			if self._inp.startsWith('\n'):
				self._inp.pop()
			return tuple(code)

		async def parseUntilLineEnd():
			await self._parser.subParser(
				self._inp, self._ELIF_OR_ELSE_OR_ENDLINE
			).parseUntilLineEnd()
			line = await Buffer.loadAsync(
				BufferRule(self._parser, self._inp).popUntil(
					self._ELIF_OR_ELSE_OR_ENDLINE
				)
			)
			self._inp.insert(0, line)

		conditions = [(tuple(self._firstConditionFrame), await popCodeBlock())]
		await parseUntilLineEnd()
		while await self._inpRule.startsWith(Value(objects.elif_)):
			await self._inpRule.pop(Value(objects.elif_), Token(' '))
			frame = await Parsed(Token(':'))(self._parser, self._inp)
			await self._inpRule.pop(Token(':'))
			conditions.append((tuple(frame), await popCodeBlock()))
			await parseUntilLineEnd()

		if await self._inpRule.startsWith(Value(objects.else_)):
			await self._inpRule.pop(Value(objects.else_), Token(':'))
			elseCode = await popCodeBlock()
		else:
			elseCode = None

		return tuple(conditions), elseCode

	async def _getFromInlineCodeBlock(self):
		async def popCodeBlock():
			await self._parser.subParser(
				self._inp, self._INLINE_IF_END
			).parseUntilLineEnd()
			codeBlock = await Buffer.loadAsync(
				BufferRule(self._parser, self._inp).popUntil(self._INLINE_IF_END)
			)
			return tuple(codeBlock)

		self._inp.pop()
		conditions = [(tuple(self._firstConditionFrame), await popCodeBlock())]

		while await self._inpRule.startsWith(Token(' '), Value(objects.elif_)):
			self._inp.pop()
			self._inp.pop()
			self._inp.pop()
			frame = await Parsed(Token(':'))(self._parser, self._inp)
			self._inp.pop()
			self._inp.pop()
			conditions.append((tuple(frame), await popCodeBlock()))

		if await self._inpRule.startsWith(Token(' '), Value(objects.else_)):
			self._inp.pop()
			self._inp.pop()
			self._inp.pop()
			self._inp.pop()

			await self._parser.subParser(self._inp, Token('\n')).parseUntilLineEnd()
			elseCode = tuple(
				await Buffer.loadAsync(
					BufferRule(self._parser, self._inp).popUntil(Token('\n'))
				)
			)
		else:
			elseCode = None

		return tuple(conditions), elseCode
