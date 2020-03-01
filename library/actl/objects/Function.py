from actl.objects.BuildClass import BuildClass
from actl.syntax import SyntaxRule, Value, Token, VARIABLE


Function = BuildClass('Function')


@Function.addMethodToClass('__call__')
def _(cls, signature, body):
	self = cls.getAttr('__super__').getAttr('__call__').call()

	self.setAttr('signature', signature)
	self.setAttr('body', body)

	return self


@Function.setAttr('__syntaxRule__')
@SyntaxRule.wrap(
	Value(Function),
	Token(' '),
	VARIABLE,
	Token('('),
	use_parser=True,
	manual_apply=True
)
def _(_, _1, conditionFrame, end):
	res = Buffer.of(While.call(conditionFrame))
	res.append(end.one())
	return res
