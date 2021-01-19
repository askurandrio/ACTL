
import os
import copy
import logging

import yaml


LOGGER = logging.getLogger('actl')
DIR_LIBRARY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Project:
	_DEFAULT_HANDLERS = {}

	def __init__(self, projectF=None, source=(), this=None):
		self._head = {'handlers': copy.copy(self._DEFAULT_HANDLERS)}

		if this is not None:
			self._head = {**self._head, 'this': this}

		if projectF is not None:
			self._head = {**self._head, 'projectF': projectF}
			source = ({'include': projectF},) + tuple(source)

		self.processSource(source)

	@property
	def this(self):
		return self._head.get('this', self)

	def processSource(self, source):
		if isinstance(source, dict):
			source = source.items()

		source = list(source)
		while source:
			cmd = source.pop(0)
			if isinstance(cmd, dict):
				lcmd = list(cmd.items())
				key, arg = lcmd.pop(0)
				assert not lcmd
			else:
				key, arg = cmd
			handlers = self['handlers']
			handlers[key](self, arg)

	def include(self, projectF):
		filename = os.path.join(DIR_LIBRARY, 'projects', f'{projectF}.yaml')
		source = yaml.load(open(filename), Loader=yaml.SafeLoader)
		subProject = type(self)(source=source, this=self.this)
		self[projectF] = subProject
		_recursiveUpdate(self._head, subProject._head)

	def __getitem__(self, keys):
		if not isinstance(keys, tuple):
			keys = (keys,)

		res = self._head
		for key in keys:
			tmpRes = res[key]
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
def _(project, arg):
	project[arg['key']] = arg['value']


@Project.addDefaultHandler('include')
def _(project, projectF):
	project.include(projectF)


@Project.addDefaultHandler('py-execExternalFunction')
def _(project, arg):
	function = importFrom(arg)
	function(project)


def _recursiveUpdate(base, new):
	for key, value in new.items():
		if isinstance(value, dict):
			base[key] = base.get(key, {})
			_recursiveUpdate(base[key], value)
		elif key not in base:
			base[key] = value


def importFrom(arg):
	globalScope = {}
	try:
		from_ = arg['from']
		import_ = arg['import']
		exec(f'from {from_} import {import_}', globalScope)
	except (KeyError, ImportError, AttributeError) as ex:
		raise RuntimeError(f'Error during getting py-execExternalFunction: {arg}') from ex

	return globalScope[import_]
