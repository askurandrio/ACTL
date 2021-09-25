from actl.objects import \
		makeClass, \
		class_ as actlClass, \
		Function as actlFunction, \
		addMethodToClass, \
		executeSyncCoroutine
from actl.opcodes import VARIABLE
from actl.syntax import SyntaxRule, Value, Token, IsInstance
from actl import asDecorator
from actl.syntax.BufferRule import BufferRule
from std.base.rules import CodeBlock
from std.base.executor.Executor import Executor, Frame


class_ = makeClass('class_', (actlClass,))


@addMethodToClass(class_, '__call__')
async def _class_call(_, name, scope):
	self = makeClass(name)

	for key, value in scope.items():
		self.setAttribute(key, value)

	return self


@asDecorator(lambda rule: class_.setAttribute('__syntaxRule__', rule))
@SyntaxRule.wrap(
	Value(class_), Token(' '), IsInstance(VARIABLE),
	useParser=True,
	manualApply=True
)
def _parseClass(parser, inp):
	inpRule = BufferRule(parser, inp)
	inpRule.pop(Value(class_), Token(' '))
	clsName = inpRule.pop(IsInstance(VARIABLE)).one().name
	inpRule.pop(Token(':'))
	body = CodeBlock(parser, inp).parse()
	cls = executeSyncCoroutine(class_.call(clsName, {'body': body}))
	inp.insert(0, [cls])


@Executor.addHandler(actlClass)
async def _actlClass__handler(executor, opcode):
	className = str(await opcode.getAttribute('__name__'))
	newClass = await class_.call(className, {})
	executor.scope, prevScope = executor.scope.child(), executor.scope
	executor.scope['__class__'] = newClass
	executor.scope[className] = newClass
	self_ = await newClass.getAttribute('__self__')
	body = await opcode.getAttribute('body')

	await Frame(body)

	for key, value in executor.scope.getDiff():
		if key in ['__class__', className, '__name__']:
			continue

		if actlFunction.isinstance_(value):
			self_[key] = value
			continue

		newClass.setAttribute(key, value)

	executor.scope = prevScope
	executor.scope[className] = newClass
