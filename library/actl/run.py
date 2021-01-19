import sys

import json

import actl


def main(projectF=None, mainF=None, source=None):
	if projectF is not None:
		project = actl.Project(projectF=projectF)
		if mainF is not None:
			project = actl.Project(source=(
				{
					'include': project
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
		extraSource = json.loads(source)
		project.processSource(extraSource)

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

	if argv:
		assert 'mainF' not in args
		args['mainF'] = argv.pop(0)

	assert not argv, argv
	return args


if __name__ == '__main__':
	main(**parseArgs())
