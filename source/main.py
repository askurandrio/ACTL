
import os
import sys
import argparse

try:
	import actl
except ImportError:
	DIR_LIBRARY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'library')
	if DIR_LIBRARY not in sys.path:
		sys.path.insert(0, DIR_LIBRARY)
	import actl


def main(args):
	if args.projectf and args.mainf:
		project = actl.Project(projectf=args.projectf)
		project['mainf',] = args.mainf
	elif args.projectf:
		project = actl.Project(source=[{'import': 'std'}])
		project['mainf',] = args.projectf
	else:
		project = actl.Project(source=[{'import': 'repl'}])
		args.repl = True
	project[('build',)]()


def build_argparser():
	parser = argparse.ArgumentParser()
	parser.add_argument('projectf', help='Code or Project file', nargs='?')
	parser.add_argument('mainf', help='Code file', nargs='?')
	parser.add_argument('--repl', help='Specify for open repl mode', action='store_true')
	parser.add_argument('--projectf', help='Project file')
	parser.add_argument('--mainf', help='Code file')
	return parser


if __name__ == '__main__':
	main(build_argparser().parse_args())
