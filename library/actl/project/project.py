import os
import logging
from functools import lru_cache

import yaml

from actl.project.projectConfig import init


LOGGER = logging.getLogger('actl')
DIR_LIBRARY = os.path.dirname(
	os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


class Project:
	def __init__(self, source):
		self._head = {}
		init(self)

		for command in source:
			self['__source__'].append(command)
			self.executeCommand(command)

	@property
	def parents(self):
		return _ProjectParentsProxy(self)

	@property
	def previous(self):
		return _ProjectPreviousProxy(self)

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
				raise

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

	def __contains__(self, key):
		try:
			self[key]
		except KeyError:
			return False
		else:
			return True

	@classmethod
	@lru_cache(maxsize=None)
	def import_(cls, projectF):
		if not os.path.isabs(projectF):
			fileName = os.path.join(DIR_LIBRARY, projectF)

			while os.path.isdir(fileName):
				fileName = os.path.join(fileName, os.path.basename(projectF))

			fileName = fileName + '.yaml'
			return cls.import_(fileName)

		with open(projectF, encoding='utf-8') as file:
			source = yaml.load(file, Loader=yaml.SafeLoader)

		source = [*source, {'setKey': {'key': 'projectF', 'value': projectF}}]
		return Project(source)

	@classmethod
	def addDefaultHandler(cls, name):
		def decorator(func):
			cls._DEFAULT_HANDLERS[name] = func
			return func

		return decorator

	def __repr__(self):
		if 'projectF' in self:
			head = 'projectF={!r}'.format(self['projectF'])
		else:
			head = 'source={}'.format(self['__source__'])
		return f'{type(self).__name__}<{head}>'


class Lazy:
	def __init__(self, evaluate):
		self.evaluate = evaluate

	def __repr__(self):
		return f'{type(self).__name__}({self.evaluate})'


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
