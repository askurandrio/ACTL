# pylint: disable=redefined-outer-name, no-member

from unittest.mock import Mock

import pytest

from actl import Project, Buffer, opcodes
from actl.objects import PyToA, Number, AToPy, While, If


def test_onlyVar(execute):
	@execute.setAfterParse
	def _(code):
		assert code == [opcodes.VARIABLE(name='var')]

	@execute.setAfterExecute
	def _():
		assert execute.scope['_'] == one

	one = Number.call(1)
	execute.scope['var'] = one

	execute('var')


def test_varWithEndLine(execute):
	@execute.setAfterParse
	def _(code):
		assert code == [opcodes.VARIABLE(name='var')]

	@execute.setAfterExecute
	def _():
		assert execute.scope['_'] == one

	one = Number.call(1)
	execute.scope['var'] = one

	execute('var\n')


def test_call(execute):
	@execute.setAfterParse
	def _(code):
		assert code == [
			opcodes.CALL_FUNCTION(dst='__IV11', function='print', typeb='(', args=[], kwargs={}),
			opcodes.VARIABLE(name='__IV11')
		]

	@execute.setAfterExecute
	def _():
		print_.assert_called_once()
		assert AToPy(execute.scope['_']) == print_.return_value

	print_ = Mock()
	execute.scope['print'] = PyToA.call(print_)

	execute('print()')


def test_callWithString(execute):
	@execute.setAfterParse
	def _(code):
		assert code == [
			opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function='String', args=['s']),
			opcodes.CALL_FUNCTION(dst='__IV12', function='print', typeb='(', args=['__IV11'], kwargs={}),
			opcodes.VARIABLE(name='__IV12')
		]

	@execute.setAfterExecute
	def _():
		print_.assert_called_once_with('s')
		assert AToPy(execute.scope['_']) == print_.return_value

	print_ = Mock()
	execute.scope['print'] = PyToA.call(print_)

	execute('print("s")')


def test_while(execute):
	@execute.setAfterParse
	def _(code):
		cycle = Buffer(code).one()

		assert cycle.getAttr('__class__').equal(While)
		assert cycle.getAttr('conditionFrame') == (
			opcodes.CALL_FUNCTION(dst='__IV11', function='cond', typeb='(', args=[], kwargs={}),
			opcodes.VARIABLE(name='__IV11')
		)
		assert cycle.getAttr('code') == (
			opcodes.CALL_FUNCTION_STATIC(dst='__IV12', function='Number', args=['1']),
			opcodes.CALL_FUNCTION(dst='__IV13', function='print', typeb='(', args=['__IV12'], kwargs={}),
			opcodes.VARIABLE(name='__IV13')
		)

	@execute.setAfterExecute
	def _():
		assert cond.call_count == 2
		print_.assert_called_once_with(1)
		assert execute.scope['_'].equal(PyToA.call(False))

	def cond_():
		called, cond_.called = cond_.called, True
		return not called

	cond_.called = False
	cond = Mock(side_effect=cond_)
	print_ = Mock()
	execute.scope['cond'] = PyToA.call(cond)
	execute.scope['print'] = PyToA.call(print_)

	execute('while cond(): print(1)')


def test_if(execute):
	@execute.setAfterParse
	def _(code):
		if_ = Buffer(code).one()
		assert if_.getAttr('__class__').equal(If)
		conditionFrame, code = Buffer(if_.getAttr('conditions')).one()
		assert conditionFrame == (
			opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function='Number', typeb='(', args=['1'], kwargs={}),
			opcodes.VARIABLE(name='__IV11')
		)
		assert code == (
			opcodes.CALL_FUNCTION_STATIC(dst='__IV12', function='Number', typeb='(', args=['2'], kwargs={}),
			opcodes.SET_VARIABLE(dst='a', src='__IV12')
		)

	@execute.setAfterExecute
	def _():
		assert execute.scope['a'].equal(PyToA.call(1))

	execute('if 1: a = 2')


def test_setVariable(execute):
	@execute.setAfterParse
	def _(code):
		assert code == [
			opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function='Number', typeb='(', args=['1'], kwargs={}),
			opcodes.SET_VARIABLE(dst='a', src='__IV11')
		]

	@execute.setAfterExecute
	def _():
		assert execute.scope['a'].equal(PyToA.call(1))

	execute('a = 1')


def test_ifElse(execute):
	@execute.setAfterParse
	def _(code):
		if_ = Buffer(code).one()
		assert if_.getAttr('__class__').equal(If)
		conditionFrame, code = Buffer(if_.getAttr('conditions')).one()
		assert conditionFrame == (
			opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function='Number', typeb='(', args=['0'], kwargs={}),
			opcodes.VARIABLE(name='__IV11')
		)
		assert code == (
			opcodes.CALL_FUNCTION_STATIC(dst='__IV12', function='Number', typeb='(', args=['1'], kwargs={}),
			opcodes.SET_VARIABLE(dst='a', src='__IV12')
		)
		assert if_.getAttr('elseCode') == (
			opcodes.CALL_FUNCTION_STATIC(
				dst='__IV13', function='Number', typeb='(', args=['2.2'], kwargs={}
			),
			opcodes.SET_VARIABLE(dst='a', src='__IV13')
		)

	@execute.setAfterExecute
	def _():
		assert execute.scope['a'].equal(PyToA.call(2.2))

	execute('if 0: a = 1 else: a = 2.2')


@pytest.fixture
def execute():
	return _Execute()


class _Execute:
	def __init__(self):
		opcodes.VARIABLE.counter.reset()

		self._project = Project('std')
		self.scope = self._project['scope']

	def setAfterParse(self, func):
		self.afterParse = func  # pylint: disable=attribute-defined-outside-init

	def setAfterExecute(self, func):
		self.afterExecute = func  # pylint: disable=attribute-defined-outside-init

	def __call__(self, inp):
		self._project['uinput'] = Buffer(inp)
		code = list(self._project['parse']())  # pylint: disable=not-callable
		self.afterParse(code)
		self._project['code'] = Buffer(code)
		self._project['execute']()  # pylint: disable=not-callable
		self.afterExecute()
