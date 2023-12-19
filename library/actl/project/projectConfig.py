import collections

from actl.utils import asDecorator
from actl.project.utils import importFrom


class InheritedDict(collections.ChainMap):
	def __init__(self, key, head, project):
		self._key = key
		self._head = head
		self._project = project

	@property
	def maps(self):
		maps = [self._head]
		for parent in self._project['__parents__']:
			maps.append(parent[self._key])
		return maps


def init(project):
	project['__parents__'] = []
	project['__source__'] = []
	project['__previous__'] = {}
	project['handlers'] = InheritedDict(
		'handlers',
		{
			'py-execExternalFunction': _pyExecExternalFunctionHandler,
			'setKey': _setKeyHandler,
			'import': _importHandler,
			'include': _includeHandler,
		},
		project,
	)


def _pyExecExternalFunctionHandler(project, arg):
	function = importFrom(arg)
	function(project)


def _setKeyHandler(project, arg):
	project[arg['key']] = arg['value']


def _importHandler(project, projectF):
	project[projectF] = project.import_(projectF)


def _includeHandler(project, projectF):
	project.executeCommand({'import': projectF})

	for command in project[projectF]['__source__']:
		if ('setKey' in command) and (command['setKey']['key'] == 'projectF'):
			continue

		project.executeCommand(command)

	project['__parents__'].append(project[projectF])
