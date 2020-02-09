from actl.objects.Object import BuildClass
from actl.syntax import SyntaxRule, Value, Token, Buffer, Or, End, Frame


While = BuildClass('While')


@While.addMethodToClass('__init__')
def _(cls, conditionFrame):
	self = cls.getAttr('__super__').getAttr('__init__').call()
	self.setAttr('conditionFrame', conditionFrame)
	return self


@While.addMethod('__useCodeBlock__')
def _(self, parser):
	cls = self.getAttr('__class__')
	newSelf = cls.call(self.getAttr('conditionFrame'))
	newSelf.setAttr('code', list(parser))
	return newSelf


@While.setAttr('__syntaxRule__')
@SyntaxRule.wrap(
	Value(While),
	Token(' '),
	Frame(':').asArg('conditionFrame'),
	Or((End,), (Token(':'),)).asArg('end')
)
def _(_, _1, conditionFrame, end):
	res = Buffer.of(While.call(list(conditionFrame)))
	if end:
		res.append(end.one())
	return res
