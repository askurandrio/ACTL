from actl import objects, Buffer
from actl.syntax import SyntaxRule, Value, Token, Frame, Or, BufferRule


If = objects.BuildClass('If', objects.If)


@If.setAttr('__syntaxRule__')
@SyntaxRule.wrap(
	Value(If),
	Token(' '),
	Frame(Token(':')),
	useParser=True,
	manualApply=True
)
class _:
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

		self._inp.pop()
		self._inp.pop()
		self._firstConditionFrame = Frame(Token(':'))(parser, self._inp)
		self._inp.pop()

		if self._useCodeBlock.isFullCodeBlock(parser, inp):
			conditions, elseCode = self._getFromFullCodeBlock()
		else:
			conditions, elseCode = self._getFromInlineCodeBlock()

		if_ = If.call(*conditions, elseCode=elseCode)
		inp.set_(Buffer.of(if_) + inp)

	@property
	def _useCodeBlock(self):
		return self._parser.rules.find('UseCodeBlock').func

	def _getFromFullCodeBlock(self):
		def popCodeBlock():
			code = self._useCodeBlock.parseFullCodeBlock(self._parser, self._inp)
			return tuple(code)

		def parseLine():
			line = self._parser.subParser(self._inp, self._ELIF_OR_ELSE_OR_ENDLINE).parseLine()
			self._inp.set_(line + self._inp)

		conditions = [(tuple(self._firstConditionFrame), popCodeBlock())]
		parseLine()
		while BufferRule(self._parser, self._inp).startsWith(Value(objects.elif_)):
			self._inp.pop()
			self._inp.pop()
			frame = Frame(Token(':'))(self._parser, self._inp)
			self._inp.pop()
			conditions.append((tuple(frame), popCodeBlock()))
			parseLine()

		if BufferRule(self._parser, self._inp).startsWith(Value(objects.else_)):
			self._inp.pop()
			self._inp.pop()
			elseCode = popCodeBlock()
		else:
			elseCode = None

		return tuple(conditions), elseCode

	def _getFromInlineCodeBlock(self):
		def popCodeBlock():
			codeBlock = self._parser.subParser(self._inp, self._INLINE_IF_END).parseLine()
			return tuple(codeBlock)

		self._inp.pop()
		conditions = [(tuple(self._firstConditionFrame), popCodeBlock())]

		while BufferRule(self._parser, self._inp).startsWith(Token(' '), Value(objects.elif_)):
			self._inp.pop()
			self._inp.pop()
			self._inp.pop()
			frame = Frame(Token(':'))(self._parser, self._inp)
			self._inp.pop()
			self._inp.pop()
			conditions.append((tuple(frame), popCodeBlock()))

		if BufferRule(self._parser, self._inp).startsWith(Token(' '), Value(objects.else_)):
			self._inp.pop()
			self._inp.pop()
			self._inp.pop()
			self._inp.pop()

			elseCode = tuple(self._parser.subParser(self._inp, Token('\n')).parseLine())
		else:
			elseCode = None

		return tuple(conditions), elseCode
