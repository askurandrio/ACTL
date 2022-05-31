from actl.utils import executeSyncCoroutine


_SIGNALS = {}
_DEFAULT = object()


def onSignal(signalName, default=_DEFAULT):
	def decorator(handler):
		if signalName not in _SIGNALS:
			_SIGNALS[signalName] = [False, []]

		if (not _SIGNALS[signalName][0]) and (default is not _DEFAULT):
			executeSyncCoroutine(handler(default))

		if _SIGNALS[signalName][0]:
			executeSyncCoroutine(handler(*_SIGNALS[signalName][1]))
			return handler

		_SIGNALS[signalName][1].append(handler)
		return handler

	return decorator


async def triggerSignal(signalName, *args):
	assert signalName in _SIGNALS, f'Nobody listens signal {signalName}'

	while _SIGNALS[signalName][1]:
		handler = _SIGNALS[signalName][1].pop(0)
		await handler(*args)

	_SIGNALS[signalName] = [True, args]
