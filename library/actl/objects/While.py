from actl.objects.Object import BuildClass
from actl.syntax import SyntaxRule, Value, Token, Buffer, Or, End, Frame


While = BuildClass('While')


@While.addMethodToClass('__init__')
def _(cls, conditionFrame):
	self = cls.getAttr('__super__').getAttr('__init__').call()
	self.setAttr('conditionFrame', conditionFrame)
	return self


@While.setAttr('__syntaxRule__')
@SyntaxRule.wrap(Value(While), Token(' '), Frame.asArg('conditionFrame'), Or((End,), (Token(':'),)))
def _(_, _1, conditionFrame):
	res = Buffer.of(While.call(list(conditionFrame)))
	return res
