import os
from contextlib import contextmanager

import pytest

from actl import DIR_LIBRARY
from actl.opcodes import CALL_FUNCTION_STATIC
from std.base.objects import Module, Import, Package


ORDER_KEY = 10


async def test_simpleImport(execute, _mockOpen, _mockIsDir):
	_mockIsDir('testModule', False)
	_mockOpen('testModule.a', 'a = 1')
	execute(
		'import testModule'
	)

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC(
			'testModule',
			Import.call,
			kwargs={'importName': 'testModule'}
		)
	]

	testModule = execute.executed.scope['testModule']
	assert Module.isinstance_(testModule)
	assert str(await testModule.getAttribute('a')) == 'Number<1>'


async def test_importPackageAndModule(execute, _mockOpen, _mockIsDir):
	_mockIsDir('testPackage', True)
	_mockIsDir('testPackage/testModule', False)
	_mockOpen('testPackage/testModule.a', 'a = 1')
	execute(
		'import testPackage.testModule'
	)

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC(
			'testPackage',
			Import.call,
			kwargs={'importName': 'testPackage.testModule'}
		)
	]

	testPackage = execute.executed.scope['testPackage']
	assert Package.isinstance_(testPackage)
	testModule = await testPackage.getAttribute('testModule')
	assert str(await testModule.getAttribute('a')) == 'Number<1>'


async def test_importFromModuleAllNames(execute, _mockOpen, _mockIsDir):
	_mockIsDir('testModule', False)
	_mockOpen('testModule.a', 'a = 1')
	execute(
		'from testModule import *'
	)

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC(
			'_tmpVarTrash',
			Import.call,
			kwargs={'fromName': 'testModule', 'importName': '*'}
		)
	]

	assert str(execute.executed.scope['a']) == 'Number<1>'


async def test_importFromModuleImportName(execute, _mockOpen, _mockIsDir):
	_mockIsDir('testModule', False)
	_mockOpen('testModule.a', 'a = 1')
	execute(
		'from testModule import a'
	)

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC(
			'_tmpVarTrash',
			Import.call,
			kwargs={'fromName': 'testModule', 'importName': 'a'}
		)
	]

	assert str(execute.executed.scope['a']) == 'Number<1>'


async def test_importPackageAndPackageAndModule(execute, _mockOpen, _mockIsDir):
	_mockIsDir('testMainPackage', True)
	_mockIsDir('testMainPackage/testPackage', True)
	_mockIsDir('testMainPackage/testPackage/testModule', False)
	_mockOpen('testMainPackage/testPackage/testModule.a', 'a = 1')
	execute(
		'import testMainPackage.testPackage.testModule'
	)

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC(
			'testMainPackage',
			Import.call,
			kwargs={'importName': 'testMainPackage.testPackage.testModule'}
		)
	]

	testMainPackage = execute.executed.scope['testMainPackage']
	testPackage = await testMainPackage.getAttribute('testPackage')
	testModule = await testPackage.getAttribute('testModule')
	assert str(await testModule.getAttribute('a')) == 'Number<1>'


async def test_importFromPackageAndPackageAndModuleAllNames(execute, _mockOpen, _mockIsDir):
	_mockIsDir('testMainPackage', True)
	_mockIsDir('testMainPackage/testPackage', True)
	_mockIsDir('testMainPackage/testPackage/testModule', False)
	_mockOpen('testMainPackage/testPackage/testModule.a', 'a = 1')
	execute(
		'from testMainPackage.testPackage.testModule import *'
	)

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC(
			'_tmpVarTrash',
			Import.call,
			kwargs={
				'fromName': 'testMainPackage.testPackage.testModule',
				'importName': '*'
			}
		)
	]

	assert str(execute.executed.scope['a']) == 'Number<1>'


async def test_importNotFound(execute, _mockIsDir, _mockIsFile):
	_mockIsDir('m404', False)
	_mockIsFile('m404.a', False)
	stdLibraryDirecory = execute.project['std/base']['libraryDirectory']
	_mockIsDir('m404', False, dirLibrary=stdLibraryDirecory)
	_mockIsFile('m404.a', False, dirLibrary=stdLibraryDirecory)

	execute('import m404')

	try:
		assert execute.executed
	except RuntimeError as ex:
		assert ex.args == ('Module m404 not found',)


class _PathChecker:
	def __init__(self, mocker, mockFunction):
		self._result = {}
		mocker.patch(mockFunction, self._check)

	def _check(self, path):
		try:
			return self._result[path]
		except KeyError as ex:
			reason = f'path<{path} is not expected, only these defined {list(self._result)}'
			raise RuntimeError(reason) from ex

	def __call__(self, path, checkResult, dirLibrary=DIR_LIBRARY):
		path = os.path.join(dirLibrary, path)
		self._result[path] = checkResult


class _DirChecker(_PathChecker):
	def __init__(self, mocker, mockFunction, mockIsFile):
		super().__init__(mocker, mockFunction)
		self._mockIsFile = mockIsFile

	def __call__(self, path, checkResult, dirLibrary=DIR_LIBRARY):
		super().__call__(path, checkResult, dirLibrary=dirLibrary)
		if checkResult:
			fullPath = os.path.join(DIR_LIBRARY, path)
			yamlPath = os.path.join(fullPath, os.path.basename(fullPath))
			self._mockIsFile(f'{yamlPath}.yaml', False)


@pytest.fixture
def _mockIsFile(mocker):
	return _PathChecker(mocker, 'os.path.isfile')


@pytest.fixture
def _mockIsDir(mocker, _mockIsFile):
	return _DirChecker(mocker, 'os.path.isdir', _mockIsFile)


@pytest.fixture
def _mockOpen(mocker, _mockIsFile):
	mockFileName = None
	mockContent = None

	@contextmanager
	def _open(fileName):
		assert mockFileName == fileName
		yield mockContent


	def setContent(fileName, content):
		nonlocal mockFileName
		nonlocal mockContent
		mockFileName = os.path.join(DIR_LIBRARY, fileName)
		mockContent = content
		_mockIsFile(fileName, True)

	mocker.patch('std.base.objects.module.open', _open)
	return setContent
