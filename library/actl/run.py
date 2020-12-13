import argparse

import json

import actl


def main(args):
	if args.mainf:
		projectf = args.projectf or 'std'
		project = actl.Project(
			projectf=projectf, source=({'include': projectf}, {'mainf': args.mainf})
		)
	elif args.projectf:
		project = actl.Project(projectf=args.projectf)
	else:
		project = actl.Project(projectf='repl')

	if args.source:
		extraSource = json.loads(args.source)
		project.processSource(extraSource)

	project['build']()


def buildArgParser():
	parser = argparse.ArgumentParser()
	parser.add_argument('--projectf', help='Project file')
	parser.add_argument('--mainf', help='Code file')
	parser.add_argument('--source', help='Extra source')
	return parser


if __name__ == '__main__':
	main(buildArgParser().parse_args())
