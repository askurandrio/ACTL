import argparse

import actl


def main(args):
	if args.projectf:
		if args.mainf:
			project = actl.Project(projectf=args.projectf)
			mainf = args.mainf
		else:
			project = actl.Project(source=[{'include': 'std'}])
			mainf = args.projectf
		project['mainf'] = mainf
	else:
		project = actl.Project(source=[{'include': 'repl'}])
	if args.data:
		data = actl.Project.yaml_load(args.data)
		project = actl.Project(source=[{'include': project}, {'include': data}])
	project['build']()


def build_argparser():
	parser = argparse.ArgumentParser()
	parser.add_argument('projectf', help='Project file', nargs='?')
	parser.add_argument('mainf', help='Code file', nargs='?')
	parser.add_argument('data', help='Data', nargs='?')
	parser.add_argument('--projectf', help='Project file')
	parser.add_argument('--mainf', help='Code file')
	parser.add_argument('--data', help='Data')
	return parser


if __name__ == '__main__':
	main(build_argparser().parse_args())