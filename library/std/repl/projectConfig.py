import pdb
import traceback

from actl.Buffer import Buffer
from std.base import Parser


def getParseInput(project):
	def parseInput(scope, input_):
		return Parser(scope, project['rules'], input_)

	return parseInput


def getInput(project):
	@Buffer.wrap
	def make():
		parser = project['buildParser']
		while True:
			if parser.applyingRule:
				msg = '... '
			else:
				msg = '>>> '

			try:
				inp = input(msg) + '\n'
			except EOFError:
				project['_build'] = False
				break

			yield from inp

	return make()


def getBuild(project):
	project['_build'] = True
	project['_catchEx'] = False

	def build():
		while project['_build']:
			try:
				project.previous['build']()
			except Exception:  # pylint: disable=broad-except
				if '_debug' in project['buildScope']:
					pdb.post_mortem()
				if project['_catchEx']:
					traceback.print_exc()
				else:
					raise

	return build
