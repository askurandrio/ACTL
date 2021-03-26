import sys

import json

import actl


def main(projectF=None, mainF=None, source=None):
	if projectF is not None:
		if mainF is None:
			project = actl.Project(projectF=projectF)
		else:
			project = actl.Project(source=(
				{
					'include': projectF
				},
				{
					'setKey': {
						'key': 'mainF',
						'value': mainF
					}
				}
			))
	elif mainF is not None:
		project = actl.Project(source=(
				{
					'include': 'std'
				},
				{
					'setKey': {
						'key': 'mainF',
						'value': mainF
					}
				}
			))
	else:
		project = actl.Project(projectF='repl')

	if source is not None:
		project.processSource(source)

	project['build']()


def parseArgs(argv=None):
	if argv is None:
		argv = sys.argv[1:]
	else:
		argv = list(argv)

	args = {}
	while argv and (argv[0] in ('--projectF', '--mainF', '--source')):
		key = argv.pop(0)[2:]
		value = argv.pop(0)
		args[key] = value

	if len(argv) == 1:
		args['mainF'] = argv.pop(0)

	if len(argv) in [2, 3]:
		args['projectF'] = argv.pop(0)
		args['mainF'] = argv.pop(0)

		if len(argv) == 1:
			source = argv.pop(0)
			args['source'] = json.loads(source)

	assert not argv, argv
	return args


if __name__ == '__main__':
	main(**parseArgs())
