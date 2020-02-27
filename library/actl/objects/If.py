from actl.Buffer import Buffer
from actl.objects.BuildClass import BuildClass
from actl.syntax import SyntaxRule, Value, Token, Frame, Or, Template


If = BuildClass('If')
elif_ = BuildClass('_Elif').call()
else_ = BuildClass('_Else').call()


@If.addMethodToClass('__call__')
def _(cls, ifCondition, *elifConditions, elseCode=None):
	self = cls.getAttr('__super__').getAttr('__call__').call()

	conditions = (ifCondition,) + elifConditions

	self.setAttr('conditions', conditions)
	if elseCode is not None:
		self.setAttr('elseCode', elseCode)

	return self


@If.setAttr('__syntaxRule__')
@SyntaxRule.wrap(
	Value(If),
	Token(' '),
	Frame(Token(':')),
	use_parser=True,
	manual_apply=True
)
class _:
	_INLINE_IF_END = Or(
		(Token(' '), Value(elif_),),
		(Value(elif_),),
		(Token(' '), Value(else_),),
		(Value(else_),),
		(Token(' '), Token('\n'),),
		(Token('\n'),)
	)

	def __init__(self, parser, inp):
		self._parser = parser
		self._inp = inp

		self._inp.pop()
		self._inp.pop()
		self._firstConditionFrame = Frame(Token(':'))(parser, self._inp)
		self._inp.pop()

		if self._useCodeBlock.isFullCodeBlock(inp):
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
			codeBlock = self._useCodeBlock.popFullCodeBlock(self._parser, self._inp)
			return tuple(codeBlock)

		conditions = [(tuple(self._firstConditionFrame), popCodeBlock())]

		while self._inp and (self._inp[0] == elif_):
			self._inp.pop()
			frame = Frame(':')(self._parser, self._inp)
			self._inp.pop()
			conditions.append((tuple(frame), popCodeBlock()))

		if self._inp and (self._inp[0] == else_):
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

		while Template(Token(' '), Value(elif_)).indexMatch(self._parser, self._inp) == 0:
			self._inp.pop()
			self._inp.pop()
			self._inp.pop()
			frame = Frame(Token(':'))(self._parser, self._inp)
			self._inp.pop()
			self._inp.pop()
			conditions.append((tuple(frame), popCodeBlock()))

		if Template(Token(' '), Value(else_)).indexMatch(self._parser, self._inp) == 0:
			self._inp.pop()
			self._inp.pop()
			self._inp.pop()
			self._inp.pop()

			elseCode = tuple(self._parser.subParser(self._inp, Token('\n')).parseLine())
		else:
			elseCode = None

		return tuple(conditions), elseCode
