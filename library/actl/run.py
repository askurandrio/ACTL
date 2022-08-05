import os
import sys
import json
import tracemalloc


def main(projectF=None, mainF=None, source=None):
	recursionLimit = os.environ.get('RECURSION_LIMIT')
	if recursionLimit is not None:
		sys.setrecursionlimit(int(recursionLimit))

	# if 'ENABLE_TRACEMALLOC' in os.environ:
	# 	tracemalloc.enable()

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

	if len(argv) == 1:
		args['mainF'] = argv.pop(0)

	if len(argv) in [2, 3]:
		args['projectF'] = argv.pop(0)
		args['mainF'] = argv.pop(0)

		if len(argv) == 1:
			args['source'] = argv.pop(0)

	assert not argv, argv
	if 'source' in args:
		args = {**args, 'source': json.loads(args['source'])}
	return args


if __name__ == '__main__':  # pragma: no cover
	main(**parseArgs(sys.argv[1:]))  # pragma: no cover
