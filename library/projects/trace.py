def getBuild(project):
	def build():
		mode = project.this['mode']
		if mode == 'printOpcodes':
			_printOpcodes(project)
		else:
			raise RuntimeError(f'Mode is unexpected: {mode}')

	return build


def _printOpcodes(project):
	for opcode in project.this['parser']:
		print(opcode)
