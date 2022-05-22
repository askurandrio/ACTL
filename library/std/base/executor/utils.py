from actl.opcodes import DynamicOpCode
from std.base.executor.Executor import Executor
from std.base.executor.frame import Frame


_BIND_EXECUTOR = DynamicOpCode.create('BIND_EXECUTOR', 'executor')


async def bindExecutor():
	opcode = _BIND_EXECUTOR(executor=None)
	await Frame((opcode,))

	return opcode.executor


def makeCoroutineResultSaver(coroutine):
	async def wrapSaveCoroutineResult(saveCoroutineResult):
		result = await coroutine

		saveCoroutineResult(result)

	return wrapSaveCoroutineResult


@Executor.addHandler(_BIND_EXECUTOR)
async def _BIND_EXECUTOR_handler(executor, opcode):
	opcode.executor = executor


class CallFrame:
	_default = object()

	def __init__(self, code):
		self._code = iter(code)

	def __await__(self):
		returnValue = self._default

		def cleanup():
			while cleanup.frames:
				frame = cleanup.frames.pop(-1)
				frame.close()

		def setReturnValue(detachedReturnValue):
			nonlocal returnValue

			while len(executor.frames) != setReturnValue.framesLength:
				cleanup.frames.insert(0, executor.frames.pop(-1))

			returnValue = detachedReturnValue
			executor.setReturnValue = setReturnValue.previusSetReturnValue

		executor = yield from bindExecutor().__await__()
		setReturnValue.framesLength = len(executor.frames) + 1
		cleanup.frames = []
		executor.setReturnValue, setReturnValue.previusSetReturnValue = (
			setReturnValue,
			executor.setReturnValue,
		)

		for opcode in self._code:
			if returnValue is not self._default:
				break

			yield opcode

		cleanup()
		if returnValue is self._default:
			raise RuntimeError('Code is empty, but returnValue also empty')

		return returnValue
