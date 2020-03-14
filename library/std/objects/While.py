from actl import objects
from actl.syntax import SyntaxRule, Value, Token, Buffer, Or, End, Frame


While = objects.BuildClass('While', objects.While)


@While.addMethod('__useCodeBlock__')
def _(self, parser):
	newSelf = self.class_.call(self.getAttr('conditionFrame'), tuple(parser))
	return newSelf


@While.setAttr('__syntaxRule__')
@SyntaxRule.wrap(
	Value(While),
	Token(' '),
	Frame(Token(':')).asArg('conditionFrame'),
	Or((End,), (Token(':'),)).asArg('end')
)
def _(_, _1, conditionFrame, end):
	res = Buffer.of(While.call(conditionFrame))
	res.append(end.one())
	return res
