from actl.objects.Object import BuildClass
from actl.opcodes import VARIABLE
from actl.syntax import SyntaxRule, Value, Token, Buffer, Or, End


While = BuildClass('While')


@While.addMethodToClass('__init__')
def _(cls, condition):
	self = cls.getAttr('__super__').getAttr('__init__').call()
	self.setAttr('condition', condition)
	return self


@While.setAttr('__syntaxRule__')
@SyntaxRule.wrap(Value(While), Token(' '), Token(VARIABLE), Or((End,), (Token(':'),)))
def _(_, _1, condition, end=None):
	res = Buffer.of(While.call(condition))
	if end is not None:
		res.append(end)
	return res
