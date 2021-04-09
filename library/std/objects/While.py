from actl import objects
from actl.Buffer import Buffer
from actl.objects.object.utils import addMethod
from actl.syntax import SyntaxRule, Value, Token, Or, End, Frame, CustomTemplate

While = objects.makeClass('While', (objects.While,))


@addMethod(While, '__useCodeBlock__')
def _(self, code):
	newSelf = self.getAttribute('__class__').call(self.getAttribute('conditionFrame'), code)
	return [newSelf]


@SyntaxRule.wrap(
	Value(While),
	Token(' '),
	CustomTemplate.asArg(Frame(Token(':')), 'conditionFrame'),
	CustomTemplate.asArg(Or((End,), (Token(':'),)), 'end')
)
def _syntaxRule(_, _1, conditionFrame, end):
	res = Buffer.of(While.call(conditionFrame))
	res.append(end.one())
	return res


While.setAttribute('__syntaxRule__', _syntaxRule)