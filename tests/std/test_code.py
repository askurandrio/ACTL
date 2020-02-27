# pylint: disable=redefined-outer-name, no-member

from unittest.mock import Mock

import pytest

from actl import Project, Buffer, opcodes
from actl.objects import PyToA, Number, AToPy, While, If


def test_onlyVar(execute):
	one = Number.call(1)
	execute.scope['var'] = one

	execute('var')

	assert execute.parsed.code == [opcodes.VARIABLE(name='var')]
	assert execute.executed.scope['_'] == one


def test_varWithEndLine(execute):
	one = Number.call(1)
	execute.scope['var'] = one

	execute('var\n')

	assert execute.parsed.code == [opcodes.VARIABLE(name='var')]
	assert execute.executed.scope['_'] == one


def test_setVariable(execute):
	execute('a = 1')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV11', function='Number', typeb='(', args=['1'], kwargs={}
		),
		opcodes.SET_VARIABLE(dst='a', src='__IV11')
	]
	assert execute.executed.scope['a'].equal(PyToA.call(1))


def test_call(execute):
	print_ = Mock()
	execute.scope['print'] = PyToA.call(print_)

	execute('print()')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION(dst='__IV11', function='print', typeb='(', args=[], kwargs={}),
		opcodes.VARIABLE(name='__IV11')
	]
	assert AToPy(execute.executed.scope['_']) == print_.return_value
	print_.assert_called_once()


def test_callWithString(execute):
	print_ = Mock()
	execute.scope['print'] = PyToA.call(print_)

	execute('print("s")')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function='String', args=['s']),
		opcodes.CALL_FUNCTION(
			dst='__IV12', function='print', typeb='(', args=['__IV11'], kwargs={}
		),
		opcodes.VARIABLE(name='__IV12')
	]
	assert AToPy(execute.executed.scope['_']) == print_.return_value
	print_.assert_called_once_with('s')


def test_float(execute):
	execute('a = 1.1')

	assert execute.parsed.code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV11', function='Number', typeb='(', args=['1.1'], kwargs={}
		),
		opcodes.SET_VARIABLE(dst='a', src='__IV11')
	]
	assert AToPy(execute.executed.scope['a']) == 1.1


def test_while(execute):
	def cond_():
		called, cond_.called = cond_.called, True
		return not called

	cond_.called = False
	cond = Mock(side_effect=cond_)
	print_ = Mock()
	execute.scope['cond'] = PyToA.call(cond)
	execute.scope['print'] = PyToA.call(print_)

	execute('while cond(): print(1)')

	cycle = execute.parsed.code.one()
	assert cycle.getAttr('__class__').equal(While)
	assert cycle.getAttr('conditionFrame') == (
		opcodes.CALL_FUNCTION(dst='__IV11', function='cond', typeb='(', args=[], kwargs={}),
		opcodes.VARIABLE(name='__IV11')
	)
	assert cycle.getAttr('code') == (
		opcodes.CALL_FUNCTION_STATIC(dst='__IV12', function='Number', args=['1']),
		opcodes.CALL_FUNCTION(
			dst='__IV13', function='print', typeb='(', args=['__IV12'], kwargs={}
		),
		opcodes.VARIABLE(name='__IV13')
	)

	assert execute.executed.scope['_'].equal(PyToA.call(False))
	assert cond.call_count == 2
	print_.assert_called_once_with(1)


def test_if(execute):
	execute('if 1: a = 2')

	if_ = Buffer(execute.parsed.code).one()
	assert if_.getAttr('__class__').equal(If)
	conditionFrame, code = Buffer(if_.getAttr('conditions')).one()
	assert conditionFrame == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV11', function='Number', typeb='(', args=['1'], kwargs={}
		),
		opcodes.VARIABLE(name='__IV11')
	)
	assert code == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV12', function='Number', typeb='(', args=['2'], kwargs={}
		),
		opcodes.SET_VARIABLE(dst='a', src='__IV12')
	)

	assert execute.executed.scope['a'].equal(PyToA.call(1))


def test_ifElif(execute):
	execute('if 0: a = 1 elif 1: a = 2')

	if_ = Buffer(execute.parsed.code).one()
	assert if_.getAttr('__class__').equal(If)
	assert if_.getAttr('conditions') == (
		(
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='__IV11', function='Number', typeb='(', args=['0'], kwargs={}
				),
				opcodes.VARIABLE(name='__IV11')
			),
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='__IV12', function='Number', typeb='(', args=['1'], kwargs={}
				),
				opcodes.SET_VARIABLE(dst='a', src='__IV12')
			)
		),
		(
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='__IV13', function='Number', typeb='(', args=['1'], kwargs={}
				),
				opcodes.VARIABLE(name='__IV13')
			),
			(
				opcodes.CALL_FUNCTION_STATIC(
					dst='__IV14', function='Number', typeb='(', args=['2'], kwargs={}
				),
				opcodes.SET_VARIABLE(dst='a', src='__IV14')
			)
		)
	)
	assert execute.executed.scope['a'].equal(PyToA.call(2.2))


def test_ifElse(execute):
	execute('if 0: a = 1 else: a = 2')

	if_ = Buffer(execute.parsed.code).one()
	assert if_.getAttr('__class__').equal(If)
	conditionFrame, code = Buffer(if_.getAttr('conditions')).one()
	assert conditionFrame == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV11', function='Number', typeb='(', args=['0'], kwargs={}
		),
		opcodes.VARIABLE(name='__IV11')
	)
	assert code == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV12', function='Number', typeb='(', args=['1'], kwargs={}
		),
		opcodes.SET_VARIABLE(dst='a', src='__IV12')
	)
	assert if_.getAttr('elseCode') == (
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV13', function='Number', typeb='(', args=['2'], kwargs={}
		),
		opcodes.SET_VARIABLE(dst='a', src='__IV13')
	)
	assert execute.executed.scope['a'].equal(PyToA.call(2.2))


@pytest.fixture
def execute():
	return _Execute()


class _Execute:
	def __init__(self):
		opcodes.VARIABLE.counter.reset()

		self._isParsed = False
		self._isExecuted = False
		self._project = Project('std')

	@property
	def scope(self):
		return self._project['scope']

	@property
	def code(self):
		return self._project['code']

	@property
	def parsed(self):
		if self._isParsed:
			return self

		code = self._project['parse']()  # pylint: disable=not-callable
		self._project['code'] = Buffer(tuple(code))
		self._isParsed = True
		return self.parsed

	@property
	def executed(self):
		if self._isExecuted:
			return self

		self._project['execute']()  # pylint: disable=not-callable
		self._isExecuted = True
		return self.executed

	def __call__(self, code):
		self._project['uinput'] = Buffer(code)
