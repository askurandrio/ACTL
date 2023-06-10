import os
from contextlib import contextmanager

import pytest

from actl import DIR_LIBRARY
from actl.objects.AToPy import AToPy
from actl.opcodes import CALL_FUNCTION_STATIC, SET_VARIABLE, GET_ATTRIBUTE
from std.base.objects import Module, import_
from std.base.objects.importDefinition import copyAlllIntoScope


ORDER_KEY = 10


async def test_simpleImport(execute, _mockFile, _mockIsDir):
	_mockIsDir('testModule', False)
	_mockFile('testModule.a', 'a = "a"')
	execute('import testModule')

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC('testModule', import_.call, staticArgs=('testModule',))
	]

	testModule = execute.executed.scope['testModule']
	assert await Module.isinstance_(testModule)
	assert str(await testModule.getAttribute('a')) == 'a'


async def test_importPackageAndModule(execute, _mockFile, _mockIsDir):
	_mockIsDir('testPackage', True)
	_mockIsDir('testPackage/testModule', False)
	_mockFile('testPackage/testModule.a', 'a = "a"')
	execute('import testPackage.testModule')

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC('testPackage', import_.call, staticArgs=('testPackage',)),
		SET_VARIABLE('_tmpVar1', 'testPackage'),
		GET_ATTRIBUTE('_tmpVar1', '_tmpVar1', 'testModule'),
	]

	testPackage = execute.executed.scope['testPackage']
	assert await Module.isinstance_(testPackage)
	testModule = await testPackage.getAttribute('testModule')
	assert str(await testModule.getAttribute('a')) == 'a'


async def test_importFromModuleAllNames(execute, _mockFile, _mockIsDir):
	_mockIsDir('testModule', False)
	_mockFile('testModule.a', 'a = "a"')
	execute('from testModule import *')

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC('_tmpVar1', import_.call, staticArgs=('testModule',)),
		CALL_FUNCTION_STATIC(
			'_', copyAlllIntoScope.call, args=('_tmpVar1', '__scope__')
		),
	]

	assert str(execute.executed.scope['a']) == 'a'


async def test_importFromModuleImportName(execute, _mockFile, _mockIsDir):
	_mockIsDir('testModule', False)
	_mockFile('testModule.a', 'a = "a"')
	execute('from testModule import a')

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC('_tmpVar1', import_.call, staticArgs=('testModule',)),
		GET_ATTRIBUTE('a', '_tmpVar1', 'a'),
	]

	assert str(execute.executed.scope['a']) == 'a'


async def test_importPackageAndPackageAndModule(execute, _mockFile, _mockIsDir):
	_mockIsDir('testMainPackage', True)
	_mockIsDir('testMainPackage/testPackage', True)
	_mockIsDir('testMainPackage/testPackage/testModule', False)
	_mockFile('testMainPackage/testPackage/testModule.a', 'a = "a"')
	execute('import testMainPackage.testPackage.testModule')

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC(
			'testMainPackage', import_.call, staticArgs=('testMainPackage',)
		),
		SET_VARIABLE('_tmpVar1', 'testMainPackage'),
		GET_ATTRIBUTE('_tmpVar1', '_tmpVar1', 'testPackage'),
		GET_ATTRIBUTE('_tmpVar1', '_tmpVar1', 'testModule'),
	]

	testMainPackage = execute.executed.scope['testMainPackage']
	testPackage = await testMainPackage.getAttribute('testPackage')
	testModule = await testPackage.getAttribute('testModule')
	assert str(await testModule.getAttribute('a')) == 'a'


async def test_importFromPackageAndPackageAndModuleAllNames(
	execute, _mockFile, _mockIsDir
):
	_mockIsDir('testMainPackage', True)
	_mockIsDir('testMainPackage/testPackage', True)
	_mockIsDir('testMainPackage/testPackage/testModule', False)
	_mockFile('testMainPackage/testPackage/testModule.a', 'a = "a"')
	execute('from testMainPackage.testPackage.testModule import *')

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC('_tmpVar1', import_.call, staticArgs=('testMainPackage',)),
		GET_ATTRIBUTE('_tmpVar1', '_tmpVar1', 'testPackage'),
		GET_ATTRIBUTE('_tmpVar1', '_tmpVar1', 'testModule'),
		CALL_FUNCTION_STATIC(
			'_', copyAlllIntoScope.call, args=('_tmpVar1', '__scope__')
		),
	]

	assert str(execute.executed.scope['a']) == 'a'


async def test_importNotFound(execute, _mockIsDir, _mockIsFile):
	for dirLibrary in execute.project['libraryDirectories']:
		_mockIsDir('m404', False, dirLibrary=dirLibrary)
		_mockIsFile('m404.a', False, dirLibrary=dirLibrary)

	execute('import m404')

	with pytest.raises(RuntimeError, match='Module m404 not found'):
		assert execute.executed


async def test_importFromAnotherProject(execute, _mockIsDir, _mockFile):
	_mockIsDir('testProject', True, True)
	_mockFile('testProject/testProject.yaml', '-  include: std/base')
	_mockIsDir('testProject/testModule', False)
	_mockFile('testProject/testModule.a', 'a = "a"')
	execute('import testProject.testModule')

	testPackage = execute.executed.scope['testProject']
	testPackageProject = AToPy(await testPackage.getAttribute('__project__'))
	assert testPackageProject['projectF'].endswith('testProject/testProject.yaml')
	testModule = await testPackage.getAttribute('testModule')
	assert testPackageProject is AToPy(await testModule.getAttribute('__project__'))
	assert str(await testModule.getAttribute('a')) == 'a'


class _PathChecker:
	def __init__(self, mocker, mockFunction):
		super().__init__()
		mocker.patch(mockFunction, self._mock)
		self._result = {}
		self._not_used = []

	def __enter__(self):
		return self

	def __exit__(self, *_):
		assert not self._not_used

	def _mock(self, path):
		try:
			result = self._result[path]
		except KeyError as ex:
			reason = (
				f'path<{path} is not expected, only these defined {list(self._result)}'
			)
			raise RuntimeError(reason) from ex

		if path in self._not_used:
			self._not_used.remove(path)
		return result

	def __call__(self, path, checkResult, dirLibrary=DIR_LIBRARY):
		path = os.path.join(dirLibrary, path)
		assert path not in list(self._result)
		self._result[path] = checkResult


class _DirChecker(_PathChecker):
	def __init__(self, mocker, mockFunction, mockIsFile):
		super().__init__(mocker, mockFunction)
		self._mockIsFile = mockIsFile

	def __call__(self, path, checkResult, isProjectDir=False, dirLibrary=DIR_LIBRARY):
		super().__call__(path, checkResult, dirLibrary=dirLibrary)

		if not checkResult:
			return

		self._mockIsFile(path, False)
		if isProjectDir:
			return

		fullPath = os.path.join(DIR_LIBRARY, path)
		yamlPath = os.path.join(fullPath, os.path.basename(fullPath))
		self._mockIsFile(f'{yamlPath}.yaml', False)


class _FileContentMock:
	def __init__(self, mocker, mockIsFile):
		super().__init__()
		self._result = {}
		self._mockIsFile = mockIsFile

		mocker.patch('std.base.objects.module.open', self._mock)
		mocker.patch('actl.project.open', self._mock)

	@contextmanager
	def _mock(self, fileName, **_):
		content = self._result[fileName]
		assert content is not None
		self._result[fileName] = None
		yield content

	def __call__(self, fileName, content):
		fileName = os.path.join(DIR_LIBRARY, fileName)
		self._result[fileName] = content
		self._mockIsFile(fileName, True)

	def __enter__(self):
		return self

	def __exit__(self, *_):
		for _, content in self._result.items():
			assert content is None


@pytest.fixture
def _mockIsFile(mocker):
	with _PathChecker(mocker, 'os.path.isfile') as mock:
		yield mock


@pytest.fixture
def _mockIsDir(mocker, _mockIsFile):
	with _DirChecker(mocker, 'os.path.isdir', _mockIsFile) as mock:
		yield mock


@pytest.fixture
def _mockFile(mocker, _mockIsFile):
	with _FileContentMock(mocker, _mockIsFile) as mock:
		yield mock
