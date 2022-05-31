from actl import opcodes
from actl.objects import While, Bool, If, AToPy, Object

from std.base.executor.frame import Frame
from std.base.executor.Executor import Executor


@Executor.addHandler(type(Object))
async def _objectHandler(executor, opcode):
	async def getHandler():
		class_ = await opcode.getAttribute('__class__')
		for parent in [class_, *await class_.getAttribute('__parents__')]:
			try:
				return executor.getHandlerFor(parent)
			except KeyError:
				pass

		raise RuntimeError(f'Handler for {opcode} not found')

	handler = await getHandler()
	return await handler(executor, opcode)


@Executor.addHandler(opcodes.VARIABLE)
async def _VARIABLE__handler(_, _1):
	pass


@Executor.addHandler(opcodes.SET_VARIABLE)
async def _SET_VARIABLE__handler(executor, opcode):
	src = executor.scope[opcode.src]

	executor.scope[opcode.dst] = src


@Executor.addHandler(opcodes.CALL_FUNCTION_STATIC)
async def _CALL_FUNCTION_STATIC__handler(executor, opcode):
	assert opcode.typeb == '(', f'{opcode.typeb} is unexpected typeb'

	args = [*opcode.staticArgs]
	for varName in opcode.args:
		args.append(executor.scope[varName])

	if isinstance(opcode.function, str):
		function = executor.scope[opcode.function].call
	else:
		function = opcode.function

	kwargs = {**opcode.staticKwargs}
	for name, varName in opcode.kwargs.items():
		kwargs[name] = executor.scope[varName]

	result = await function(*args, **kwargs)

	executor.scope[opcode.dst] = result


@Executor.addHandler(opcodes.CALL_FUNCTION)
async def _CALL_FUNCTION__handler(executor, opcode):
	function = executor.scope[opcode.function]
	assert opcode.typeb == '('
	args = [executor.scope[varName] for varName in opcode.args]
	kwargs = {
		argName: executor.scope[varName] for argName, varName in opcode.kwargs.items()
	}

	result = await function.call(*args, **kwargs)

	executor.scope[opcode.dst] = result


@Executor.addHandler(opcodes.RETURN)
async def _RETURN__handler(executor, opcode):
	returnValue = executor.scope[opcode.var]
	executor.setReturnValue(returnValue)


@Executor.addHandler(opcodes.CALL_OPERATOR)
async def _CALL_OPERATOR__handler(executor, opcode):
	first = executor.scope[opcode.first]
	second = executor.scope[opcode.second]

	pyFirst = AToPy(first)
	pySecond = AToPy(second)
	pyResult = eval(  # pylint: disable=eval-used
		f'pyFirst {opcode.operator} pySecond',
		{'pyFirst': pyFirst, 'pySecond': pySecond},
	)

	resultClass = await first.getAttribute('__class__')
	result = await resultClass.call(pyResult)

	executor.scope[opcode.dst] = result


@Executor.addHandler(opcodes.GET_ATTRIBUTE)
async def _GET_ATTRIBUTE__handler(executor, opcode):
	object_ = executor.scope[opcode.object]
	attribute = opcode.attribute

	executor.scope[opcode.dst] = await object_.getAttribute(attribute)


@Executor.addHandler(opcodes.SET_ATTRIBUTE)
async def _SET_ATTRIBUTE__handler(executor, opcode):
	object_ = executor.scope[opcode.object]
	attribute = opcode.attribute
	src = executor.scope[opcode.src]

	await object_.setAttribute(attribute, src)


@Executor.addHandler(While)
async def _While__handler(executor, opcode):
	conditionFrame = await opcode.getAttribute('conditionFrame')
	resultConditionName = conditionFrame[-1].name
	code = await opcode.getAttribute('code')

	while True:
		await Frame(conditionFrame)
		res = await Bool.call(executor.scope[resultConditionName])
		if not AToPy(res):
			break

		await Frame(code)


@Executor.addHandler(If)
async def _If__handler(executor, opcode):
	for conditionFrame, code in await opcode.getAttribute('conditions'):
		await Frame(conditionFrame)
		res = executor.scope[conditionFrame[-1].name]
		res = await Bool.call(res)
		if AToPy(res):
			await Frame(code)
			return

	if await opcode.hasAttribute('elseCode'):
		elseCode = await opcode.getAttribute('elseCode')
		await Frame(elseCode)
