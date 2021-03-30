from actl import objects
from actl.Buffer import Buffer
from actl.syntax import SyntaxRule, Value, Token, Or, End, Frame, CustomTemplate

While = objects.BuildClass('While', objects.While)


@While.addMethod('__useCodeBlock__')
def _(self, parser):
	newSelf = self.getAttribute('__class__').call(self.getAttribute('conditionFrame'), tuple(parser))
	return newSelf


@While.setAttribute('__syntaxRule__')
@SyntaxRule.wrap(
	Value(While),
	Token(' '),
	CustomTemplate.asArg(Frame(Token(':')), 'conditionFrame'),
	CustomTemplate.asArg(Or((End,), (Token(':'),)), 'end')
)
def _(_, _1, conditionFrame, end):
	res = Buffer.of(While.call(conditionFrame))
	res.append(end.one())
	return res
