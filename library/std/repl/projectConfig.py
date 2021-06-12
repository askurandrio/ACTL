import pdb
import traceback

from actl.Buffer import Buffer
from std.base import Parser


def getParseInput(project):
	def parseInput(scope, input_):
		return Parser(scope, project.this['rules'], input_)

	return parseInput


def getInput(project):
	@Buffer.wrap
	def make():
		parser = project.this['buildParser']
		while True:
			if parser.applyingRule:
				msg = '... '
			else:
				msg = '>>> '

			try:
				inp = input(msg) + '\n'
			except EOFError:
				project.this['_build'] = False
				break

			yield from inp

	return make()


def getBuild(project):
	project.this['_build'] = True
	project.this['_catchEx'] = False

	def build():
		while project.this['_build']:
			try:
				project.this['std/base', 'build']()
			except Exception:  # pylint: disable=broad-except
				if '_debug' in project.this['buildScope']:
					pdb.post_mortem()
				if project.this['_catchEx']:
					traceback.print_exc()
				else:
					raise

	return build
