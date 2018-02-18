
import sys
import argparse
import traceback

from actl import Project


def repl(project):
	while True:
		print('>>> ', end='')
		sys.stdout.flush()
		code = None
		uinput = ''
		try:
			for line in sys.stdin:
				if not line.strip():
					break
				uinput += line
				if line[0] == ' ':
					continue
				code = project.build(string=uinput)
				if not code.is_matching():
					break
			if code is not None:
				print('\n')
				project.translator.exec(code)
		except Exception: #pylint: disable=W0703
			traceback.print_exc()


def main(args):
	if args.projectf and args.mainf:
		project = Project(projectf=args.projectf)
		project.set('mainf', value=args.mainf)
	elif args.projectf:
		project = Project.create_temp()
		project.set('mainf', value=args.projectf)
	else:
		project = Project(data={'from':'repl'})
		args.repl = True

	if args.repl:
		repl(project)
	else:
		code = project.build()
		project.translator.write(code)


def build_argparser():
	parser = argparse.ArgumentParser()
	parser.add_argument('projectf', help='Code or Project file', nargs='?')
	parser.add_argument('mainf', help='Code or Project file', nargs='?')
	parser.add_argument('--repl', help='Specify for open repl mode', action='store_true')
	parser.add_argument('--projectf', help='Project file')
	parser.add_argument('--mainf', help='Code file')
	return parser

if __name__ == '__main__':
	main(build_argparser().parse_args())
