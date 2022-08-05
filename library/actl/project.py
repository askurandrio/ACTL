import copy
import os
from collections import ChainMap
import logging
import importlib
from functools import lru_cache

import yaml


LOGGER = logging.getLogger('actl')
DIR_LIBRARY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Project:
	_DEFAULT_HANDLERS = {}

	def __init__(self):
		self._head = {'__parents__': [], '__source__': [], '__previous__': {}}
		self['handlers'] = InheritedDict(
			'handlers', copy.copy(self._DEFAULT_HANDLERS), self
		)

	@property
	def parents(self):
		return _ProjectParentsProxy(self)

	@property
	def previous(self):
		return _ProjectPreviousProxy(self)

	def processSource(self, source):
		for command in source:
			self['__source__'].append(command)
			self.executeCommand(command)

	def executeCommand(self, command):
		items = iter(command.items())
		handlerName, argument = next(items)
		try:
			next(items)
		except StopIteration:
			pass
		else:
			raise RuntimeError(f'len({command}) should be 1')
		handler = self['handlers'][handlerName]
		handler(self, argument)

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

	def __setitem__(self, key, value):
		if key in self._head:
			self.previous.append(key, self._head[key])

		self._head[key] = value

	def __delitem__(self, key):
		del self._head[key]

	@classmethod
	@lru_cache(maxsize=None)
	def loadProject(cls, projectF):
		if not os.path.isabs(projectF):
			fileName = os.path.join(DIR_LIBRARY, projectF)

			while os.path.isdir(fileName):
				fileName = os.path.join(fileName, os.path.basename(projectF))

			fileName = fileName + '.yaml'
			return cls.loadProject(fileName)

		with open(projectF, encoding='utf-8') as file:
			source = yaml.load(file, Loader=yaml.SafeLoader)
			source = [*source, {'setKey': {'key': 'projectF', 'value': projectF}}]

		subProject = Project()
		subProject.processSource(source)
		return subProject

	@classmethod
	def addDefaultHandler(cls, name):
		def decorator(func):
			cls._DEFAULT_HANDLERS[name] = func
			return func

		return decorator

	def __repr__(self):
		if 'projectF' in self._head:
			head = 'projectF={!r}'.format(self['projectF'])
		else:
			head = 'source={}'.format(self['__source__'])
		return f'{type(self).__name__}<{head}>'


class Lazy:
	def __init__(self, evaluate):
		self.evaluate = evaluate

	def __repr__(self):
		return f'{type(self).__name__}({self.evaluate})'


@Project.addDefaultHandler('setKey')
def _setKeyHandler(project, arg):
	project[arg['key']] = arg['value']


@Project.addDefaultHandler('include')
def _includeHandler(project, projectF):
	subProject = project.loadProject(projectF)

	for command in subProject['__source__']:
		if ('setKey' in command) and (command['setKey']['key'] == 'projectF'):
			continue

		project.executeCommand(command)

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
		raise RuntimeError(
			f'Error during getting py-execExternalFunction: {arg}'
		) from ex

	try:
		from_ = importlib.import_module(from_)
	except ImportError as ex:
		raise RuntimeError(
			f'Error importing from_ at py-execExternalFunction: {arg}'
		) from ex

	try:
		return getattr(from_, import_)
	except AttributeError as ex:
		raise RuntimeError(
			f'Error getting {import_} at py-execExternalFunction: {arg}'
		) from ex


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


class _ProjectPreviousProxy:
	def __init__(self, project):
		self._project = project

	def append(self, key, value):
		previous = self._project['__previous__']
		if key not in previous:
			previous[key] = []

		previous[key].append(value)

	def __getitem__(self, key):
		previous = self._project['__previous__']
		result = previous[key][-1]

		if isinstance(result, Lazy):
			previous[key][-1] = result.evaluate()
			return self[key]

		return result
