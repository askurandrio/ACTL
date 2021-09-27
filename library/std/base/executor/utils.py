from actl.opcodes import DynamicOpCode
from std.base.executor.Executor import Executor


_BIND_EXECUTOR = DynamicOpCode.create('BIND_EXECUTOR', 'executorTrap')


async def bindExecutor():
	executorTrap = _ExecutorTrap()
	await executorTrap

	return executorTrap.executor


class _ExecutorTrap:
	def __init__(self):
		self.executor = None

	def __await__(self):
		yield _BIND_EXECUTOR(executorTrap=self)


@Executor.addHandler(_BIND_EXECUTOR)
async def _BIND_EXECUTOR_handler(executor, opcode):
	opcode.executorTrap.executor = executor


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

		def return_(detachedReturnValue):
			nonlocal returnValue

			while len(executor.frames) != return_.framesLength:
				cleanup.frames.insert(0, executor.frames.pop(-1))

			returnValue = detachedReturnValue
			executor.return_ = return_.oldExecutorReturn

		executor = yield from bindExecutor().__await__()
		return_.framesLength = len(executor.frames) + 1
		cleanup.frames = []
		executor.return_, return_.oldExecutorReturn = return_, executor.return_

		for opcode in self._code:
			if returnValue is not self._default:
				break

			yield opcode

		cleanup()
		if returnValue is self._default:
			raise RuntimeError('Code is empty, but returnValue also empty')

		return returnValue
