def getBuild(project):
	def build():
		mode = project.this['mode']
		if mode == 'printOpcodes':
			print(*project.this['parser'], sep='\n')
		else:
			raise RuntimeError(f'Mode is unexpected: {mode}')

	return build
