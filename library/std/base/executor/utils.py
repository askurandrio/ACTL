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
			while len(executor.frames) != cleanup.framesLength:
				frame = executor.frames.pop(-1)
				frame.close()

			executor.return_ = cleanup.oldExecutorReturn

		def return_(detachedReturnValue):
			nonlocal returnValue
			returnValue = detachedReturnValue

		executor = yield from bindExecutor().__await__()
		cleanup.framesLength = len(executor.frames)
		executor.return_, cleanup.oldExecutorReturn = return_, executor.return_

		for opcode in self._code:
			if returnValue is not self._default:
				break

			yield opcode

		cleanup()
		if returnValue is self._default:
			raise RuntimeError('Code is empty, but returnValue also empty')

		return returnValue
