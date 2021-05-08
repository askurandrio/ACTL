import os
from contextlib import contextmanager

import pytest

from actl import DIR_LIBRARY
from actl.opcodes import CALL_FUNCTION_STATIC
from std.base.objects import Module
from std.base.objects.import_ import import_


def test_simpleImport(execute, _mockedModule):
	_mockedModule('testModule', 'a = 1')
	execute(
		'import testModule'
	)

	assert execute.parsed.code == [
		CALL_FUNCTION_STATIC('testModule', import_.call.obj, args=['testModule'])
	]

	testModule = execute.executed.scope['testModule']
	assert testModule.isinstance_(Module)
	assert str(testModule.getAttribute.obj('a').obj) == 'Number<1>'


@pytest.fixture
def _mockedModule(mocker):
	mockFileName = None
	mockContent = None

	@contextmanager
	def _open(fileName):
		assert mockFileName == fileName
		yield mockContent


	def setContent(fileName, content):
		nonlocal mockFileName
		nonlocal mockContent
		mockFileName = os.path.join(DIR_LIBRARY, f'{fileName}.a')
		mockContent = content

	mocker.patch('std.base.objects.import_.open', _open)
	return setContent
