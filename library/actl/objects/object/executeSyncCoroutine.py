
def executeSyncCoroutine(coroutine):
	generator = coroutine.__await__()

	try:
		next(generator)
	except StopIteration as ex:
		if ex.args:
			return ex.args[0]
		return None
	else:
		raise RuntimeError('Generator do not stopped')
