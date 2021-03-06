from actl import objects
from actl.Buffer import Buffer
from actl.syntax import SyntaxRule, Value, Token, Frame, Or, BufferRule
from std.rules import UseCodeBlock

If = objects.BuildClass('If', objects.If)


class IfSyntax:
	_INLINE_IF_END = Or(
		(Token(' '), Value(objects.elif_),),
		(Value(objects.elif_),),
		(Token(' '), Value(objects.else_),),
		(Value(objects.else_),),
		(Token(' '), Token('\n'),),
		(Token('\n'),)
	)
	_ELIF_OR_ELSE_OR_ENDLINE = Or(
		(Value(objects.elif_),),
		(Value(objects.else_),),
		(Token('\n'),)
	)

	def __init__(self, parser, inp):
		self._parser = parser
		self._inp = inp

		self._inpRule.pop(Value(If), Token(' '))
		self._firstConditionFrame = Frame(Token(':'))(parser, self._inp)
		self._inpRule.pop(Token(':'))

	def parse(self):
		if UseCodeBlock.isFullCodeBlock(self._parser, self._inp):
			conditions, elseCode = self._getFromFullCodeBlock()
		else:
			conditions, elseCode = self._getFromInlineCodeBlock()
		if_ = If.call(*conditions, elseCode=elseCode)
		return Buffer.of(if_)

	@property
	def _inpRule(self):
		return BufferRule(self._parser, self._inp)

	def _getFromFullCodeBlock(self):
		def popCodeBlock():
			code = Buffer(UseCodeBlock.parseFullCodeBlock(self._parser, self._inp))
			if self._inp.startswith('\n'):
				self._inp.pop()
			return tuple(code)

		def parseLine():
			self._parser.subParser(self._inp, self._ELIF_OR_ELSE_OR_ENDLINE).parseLine()
			line = BufferRule(self._parser, self._inp).popUntil(self._ELIF_OR_ELSE_OR_ENDLINE)
			self._inp.insert(0, line)

		conditions = [(tuple(self._firstConditionFrame), popCodeBlock())]
		parseLine()
		while self._inpRule.startsWith(Value(objects.elif_)):
			self._inpRule.pop(Value(objects.elif_), Token(' '))
			frame = Frame(Token(':'))(self._parser, self._inp)
			self._inpRule.pop(Token(':'))
			conditions.append((tuple(frame), popCodeBlock()))
			parseLine()

		if self._inpRule.startsWith(Value(objects.else_)):
			self._inpRule.pop(Value(objects.else_), Token(':'))
			elseCode = popCodeBlock()
		else:
			elseCode = None

		return tuple(conditions), elseCode

	def _getFromInlineCodeBlock(self):
		def popCodeBlock():
			self._parser.subParser(self._inp, self._INLINE_IF_END).parseLine()
			codeBlock = BufferRule(self._parser, self._inp).popUntil(self._INLINE_IF_END)
			return tuple(codeBlock)

		self._inp.pop()
		conditions = [(tuple(self._firstConditionFrame), popCodeBlock())]

		while self._inpRule.startsWith(Token(' '), Value(objects.elif_)):
			self._inp.pop()
			self._inp.pop()
			self._inp.pop()
			frame = Frame(Token(':'))(self._parser, self._inp)
			self._inp.pop()
			self._inp.pop()
			conditions.append((tuple(frame), popCodeBlock()))

		if self._inpRule.startsWith(Token(' '), Value(objects.else_)):
			self._inp.pop()
			self._inp.pop()
			self._inp.pop()
			self._inp.pop()

			self._parser.subParser(self._inp, Token('\n')).parseLine()
			elseCode = tuple(BufferRule(self._parser, self._inp).popUntil(Token('\n')))
		else:
			elseCode = None

		return tuple(conditions), elseCode


@If.setAttr('__syntaxRule__')
@SyntaxRule.wrap(
	Value(If),
	Token(' '),
	Frame(Token(':')),
	useParser=True,
	manualApply=True
)
def _(parser, inp):
	return IfSyntax(parser, inp).parse()
