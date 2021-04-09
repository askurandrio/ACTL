from actl.objects import makeClass, class_ as actlClass, addMethodToClass
from actl.opcodes import CALL_FUNCTION_STATIC, VARIABLE
from actl.syntax import SyntaxRule, Value, Token, IsInstance, BreakPoint
from actl import asDecorator


class_ = makeClass('class_', (actlClass,))


@addMethodToClass(class_, '__call__')
def _makeClass(_, name):
	return makeClass(name)


@asDecorator(lambda rule: class_.setAttribute('__syntaxRule__', rule))
@SyntaxRule.wrap(
	Value(class_), Token(' '), IsInstance(VARIABLE),
	useParser=True
)
def _parseClass(_, _1, classNameVar, parser):
	className = classNameVar.name

	parser.define(CALL_FUNCTION_STATIC(dst=className, function=class_.call, args=[className,]))

	return [classNameVar]
