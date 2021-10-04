import copy
import os
from collections import ChainMap
import logging
import importlib

import yaml


LOGGER = logging.getLogger('actl')
DIR_LIBRARY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Project:
	_DEFAULT_HANDLERS = {}

	def __init__(self, source=None, this=None):
		self._head = {}
		self['__parents__'] = []
		self['handlers'] = InheritedDict(
			'handlers',
			copy.copy(self._DEFAULT_HANDLERS),
			self
		)

		if this is not None:
			self.processSource([
				{
					'setKey': {
						'key': 'this',
						'value': this
					}
				}
			])

		if source:
			self.processSource(source)

	@property
	def this(self):
		return self._head.get('this', self)

	@property
	def parents(self):
		return _ProjectParentsProxy(self)

	def processSource(self, source):
		assert isinstance(source, list), source

		while source:
			command = source.pop(0)
			assert isinstance(command, dict), command
			assert len(command) == 1, command
			handlerName, arg = next(iter(command.items()))
			handler = self['handlers'][handlerName]
			handler(self, arg)

	def __getitem__(self, keys):
		if not isinstance(keys, tuple):
			keys = (keys,)

		res = self._head
		for key in keys:
			try:
				tmpRes = res[key]
			except KeyError:
				if self._head is not res:
					raise
				if key == '__parents__':
					raise
				tmpRes = self.parents[key]

			if isinstance(tmpRes, Lazy):
				tmpRes = tmpRes.evaluate()
				res[key] = tmpRes
			res = tmpRes

		return res

	def __setitem__(self, keys, value):
		if isinstance(keys, str):
			keys = (keys,)
		base = self._head
		for key in keys[:-1]:
			base = base[key]
		base[keys[-1]] = value

	def __delitem__(self, key):
		del self._head[key]

	@classmethod
	def addDefaultHandler(cls, name):
		def decorator(func):
			cls._DEFAULT_HANDLERS[name] = func
			return func
		return decorator

	def __repr__(self):
		if 'projectF' in self._head:
			head = 'projectF={!r}'.format(self._head['projectF'])
		else:
			head = f'source={self._head}'
		return f'{type(self).__name__}({head})'


class Lazy:
	def __init__(self, evaluate):
		self.evaluate = evaluate


@Project.addDefaultHandler('setKey')
def _setKeyHandler(project, arg):
	project[arg['key']] = arg['value']


@Project.addDefaultHandler('include')
def _includeHandler(project, projectF):
	fileName = os.path.join(DIR_LIBRARY, projectF)

	while os.path.isdir(fileName):
		fileName = os.path.join(fileName, os.path.basename(projectF))

	fileName = fileName + '.yaml'
	with open(fileName) as file:
		source = yaml.load(file, Loader=yaml.SafeLoader)
		source = [
			*source,
			{
				'setKey': {
					'key': 'projectF',
					'value': 'projectF'
				}
			}
		]

	subProject = Project(source=source, this=project.this)
	project[projectF] = subProject
	project['__parents__'].append(subProject)


@Project.addDefaultHandler('py-execExternalFunction')
def _pyExecExtrnalFunctionHandler(project, arg):
	function = importFrom(arg)
	function(project)


def importFrom(arg):
	try:
		from_ = arg['from']
		import_ = arg['import']
	except KeyError as ex:
		raise RuntimeError(f'Error during getting py-execExternalFunction: {arg}') from ex

	try:
		from_ = importlib.import_module(from_)
	except ImportError as ex:
		raise RuntimeError(f'Error importing from_ at py-execExternalFunction: {arg}') from ex

	try:
		return getattr(from_, import_)
	except AttributeError as ex:
		raise RuntimeError(f'Error getting {import_} at py-execExternalFunction: {arg}') from ex


class _ProjectParentsProxy:
	def __init__(self, project):
		self._project = project

	def __getitem__(self, key):
		for parent in self._project['__parents__']:
			try:
				return parent[key]
			except KeyError:
				pass

		raise KeyError(f'This key not found: {key}')


class InheritedDict(ChainMap):
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
