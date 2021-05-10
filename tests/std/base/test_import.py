import os
from contextlib import contextmanager

import pytest

from actl import DIR_LIBRARY
from actl.opcodes import CALL_FUNCTION_STATIC
from std.base.objects import Module, Import


ORDER_KEY = 10


def test_simpleImport(execute, _mockOpen, _mockIsDir):
	_mockIsDir('testModule', False)
	_mockOpen('testModule.a', 'a = 1')
	execute(
		'import testModule'
	)

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC(
			'testModule',
			Import.call.obj,
			kwargs={'importName': 'testModule'}
		)
	]

	testModule = execute.executed.scope['testModule']
	assert testModule.isinstance_(Module)
	assert str(testModule.getAttribute('a').obj) == 'Number<1>'


def test_importPackageAndModule(execute, _mockOpen, _mockIsDir):
	_mockIsDir('testPackage', True)
	_mockIsDir('testPackage/testModule', False)
	_mockOpen('testPackage/testModule.a', 'a = 1')
	execute(
		'import testPackage.testModule'
	)

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC(
			'testPackage',
			Import.call.obj,
			kwargs={'importName': 'testPackage.testModule'}
		)
	]

	testPackage = execute.executed.scope['testPackage']
	assert testPackage.isinstance_(Module)
	testModule = testPackage.getAttribute('testModule').obj
	assert str(testModule.getAttribute('a').obj) == 'Number<1>'


def test_importFromModuleAllNames(execute, _mockOpen, _mockIsDir):
	_mockIsDir('testModule', False)
	_mockOpen('testModule.a', 'a = 1')
	execute(
		'from testModule import *'
	)

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC(
			'_tmpVarTrash',
			Import.call.obj,
			kwargs={'fromName': 'testModule', 'importName': '*'}
		)
	]

	assert str(execute.executed.scope['a']) == 'Number<1>'


def test_importFromModuleImportName(execute, _mockOpen, _mockIsDir):
	_mockIsDir('testModule', False)
	_mockOpen('testModule.a', 'a = 1')
	execute(
		'from testModule import a'
	)

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC(
			'_tmpVarTrash',
			Import.call.obj,
			kwargs={'fromName': 'testModule', 'importName': 'a'}
		)
	]

	assert str(execute.executed.scope['a']) == 'Number<1>'


def test_importPackageAndPackageAndModule(execute, _mockOpen, _mockIsDir):
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
			Import.call.obj,
			kwargs={'importName': 'testMainPackage.testPackage.testModule'}
		)
	]

	testMainPackage = execute.executed.scope['testMainPackage']
	testPackage = testMainPackage.getAttribute('testPackage').obj
	testModule = testPackage.getAttribute('testModule').obj
	assert str(testModule.getAttribute('a').obj) == 'Number<1>'


def test_importFromPackageAndPackageAndModuleAllNames(execute, _mockOpen, _mockIsDir):
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
			Import.call.obj,
			kwargs={
				'fromName': 'testMainPackage.testPackage.testModule',
				'importName': '*'
			}
		)
	]

	assert str(execute.executed.scope['a']) == 'Number<1>'


@pytest.fixture
def _mockOpen(mocker):
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

	mocker.patch('std.base.objects.module.open', _open)
	return setContent


@pytest.fixture
def _mockIsDir(mocker):
	result = {}

	def isDir(path):
		return result[path]

	def addResult(path, checkResult):
		path = os.path.join(DIR_LIBRARY, path)
		result[path] = checkResult

	mocker.patch('os.path.isdir', isDir)
	return addResult
