
def executeSyncCoroutine(coroutine):
	generator = coroutine.__await__()

	try:
		opcode = next(generator)
	except StopIteration as ex:
		if ex.args:
			return ex.args[0]
		return None
	else:
		raise RuntimeError(f'Generator do not stopped. Info<opcode={opcode}, coroutine={coroutine}>')
