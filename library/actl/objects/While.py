from actl.objects.BuildClass import BuildClass
from actl.syntax import SyntaxRule, Value, Token, Buffer, Or, End, Frame

While = BuildClass('While')


@While.addMethodToClass('__call__')
def _(cls, conditionFrame, code=None):
	self = cls.getAttr('__super__').getAttr('__call__').call()

	self.setAttr('conditionFrame', conditionFrame)
	if code is not None:
		self.setAttr('code', code)

	return self


@While.addMethod('__useCodeBlock__')
def _(self, parser):
	cls = self.getAttr('__class__')
	newSelf = cls.call(self.getAttr('conditionFrame'), tuple(parser))
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
	if end:
		res.append(end.one())
	return res
