import sys

import yaml


def main(projectF=None, mainF=None, source=None):
	if projectF is None:
		if mainF is None:
			projectF = 'std/repl'
		else:
			projectF = 'std'

	projectSource = [{'include': projectF}]

	if mainF is not None:
		projectSource = [*projectSource, {'setKey': {'key': 'mainF', 'value': mainF}}]

	if source is not None:
		projectSource = [*projectSource, *source]

	from actl import Project

	project = Project()
	project.processSource(projectSource)
	project['build']()


def parseArgs(argv):
	args = {}

	while argv and (argv[0] in ('--projectF', '--mainF', '--source')):
		key = argv.pop(0)[2:]
		value = argv.pop(0)
		args[key] = value

	if (
		argv
		and argv[0].endswith('.a')
		and ('mainF' not in args)
		and ('projectF' not in args)
	):
		args['projectF'] = 'std'
		args['mainF'] = argv.pop(0)

	if 'source' in args:
		args['source'] = yaml.safe_load(args['source'])
	else:
		args['source'] = ()

	args['source'] = ({'setKey': {'key': 'argv', 'value': argv}}, *args['source'])

	return args


if __name__ == '__main__':  # pragma: no cover
	main(**parseArgs(sys.argv[1:]))  # pragma: no cover
