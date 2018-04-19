
import os
import sys
import argparse
import traceback

try:
	import actl
except ImportError:
	DIR_LIBRARY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'library')
	if DIR_LIBRARY not in sys.path:
		sys.path.insert(0, DIR_LIBRARY)
	import actl



def repl(project):
	while True:
		print('>>> ', end='')
		sys.stdout.flush()
		uinput = ''
		try:
			while True:
				try:
					line = input('')
				except EOFError:
					raise
				else:
					uinput += line
					if line and (line[0] == ' '):
						print('... ')
						continue
				finally:
					project['uinput',] = uinput
					project['build',]()
			project['run',]()
		except EOFError:
			project['run',]()
			break
		except Exception: #pylint: disable=W0703
			traceback.print_exc()
			break


def main(args):
	if args.projectf and args.mainf:
		project = actl.Project(projectf=args.projectf)
		project['mainf',] = args.mainf
	elif args.projectf:
		project = actl.Project(data={'from':'std'})
		project['mainf',] = args.projectf
	else:
		project = actl.Project(data={'from':'repl'})
		args.repl = True

	if args.repl:
		repl(project)
	else:		
		project['build',]()


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
