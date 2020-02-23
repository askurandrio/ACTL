from actl.Buffer import Buffer
from actl.objects.BuildClass import BuildClass
from actl.syntax import SyntaxRule, Value, Token, Frame

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
	Frame(':'),
	use_parser=True,
	manual_apply=True
)
def _(parser, inp):
	inp.pop()
	inp.pop()
	frame = Frame(':')(parser, inp)
	inp.pop()

	popCodeBlock = parser.rules.find('UseCodeBlock').func.popCodeBlock

	conditions = [(tuple(frame), tuple(popCodeBlock(parser, inp)))]

	while inp and (inp[0] == elif_):
		inp.pop()
		frame = Frame(':')(parser, inp)
		inp.pop()
		conditions.append((tuple(frame), tuple(popCodeBlock(parser, inp))))

	elseCode = None
	if inp and (inp[0] == else_):
		inp.pop()
		elseCode = tuple(popCodeBlock(parser, inp))

	if_ = If.call(*conditions, elseCode=elseCode)

	inp.set_(Buffer.of(if_) + inp)
