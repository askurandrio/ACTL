# pylint: disable=redefined-outer-name

import pytest

from actl import Parser, opcodes, Project, Buffer
from actl.objects import While


@pytest.fixture
def parse():
	def _parse(inp):
		project = Project('std')
		opcodes.VARIABLE.counter.reset()
		inp = Buffer(inp)
		result = Buffer(Parser(project['scope'], project['rules'], inp))
		return result

	return _parse


def test_onlyVar(parse):
	res = parse('var')

	assert res == [opcodes.VARIABLE(name='var')]


def test_varWithEndLine(parse):
	res = parse('var\n')

	assert res == [opcodes.VARIABLE(name='var')]


def test_call(parse):
	assert parse("print()") == [
		opcodes.CALL_FUNCTION(dst='__IV11', function='print', typeb='(', args=[], kwargs={}),
		opcodes.VARIABLE(name='__IV11')
	]


def test_call_with_empty_string(parse):
	assert parse("print('')") == [
		opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function='String', args=['']),
		opcodes.CALL_FUNCTION(dst='__IV12', function='print', typeb='(', args=['__IV11'], kwargs={}),
		opcodes.VARIABLE(name='__IV12')
	]


def test_call_with_string(parse):
	assert parse("print('s')") == [
		opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function='String', args=['s']),
		opcodes.CALL_FUNCTION(dst='__IV12', function='print', typeb='(', args=['__IV11'], kwargs={}),
		opcodes.VARIABLE(name='__IV12')
	]


def test_while(parse):
	cycle = parse('while True').one()

	assert cycle.getAttr('__class__').equal(While)
	assert cycle.getAttr('conditionFrame') == [
		opcodes.VARIABLE(name='True')
	]


def test_whileWithSimpleCode(parse):
	cycle = parse('while True: True').one()

	assert cycle.getAttr('__class__').equal(While)
	assert cycle.getAttr('conditionFrame') == [opcodes.VARIABLE(name='True')]
	assert cycle.getAttr('code') == [opcodes.VARIABLE(name='True')]


def test_whileWithConditionIsCallFunction(parse):
	cycle = parse('while print("")').one()

	assert cycle.getAttr('__class__').equal(While)
	assert cycle.getAttr('conditionFrame') == [
		opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function='String', typeb='(', args=[''], kwargs={}),
		opcodes.CALL_FUNCTION(dst='__IV12', function='print', typeb='(', args=['__IV11'], kwargs={}),
		opcodes.VARIABLE(name='__IV12')
	]


def test_whileWithSimplePrint(parse):
	cycle = parse('while True: print()').one()

	assert cycle.getAttr('__class__').equal(While)
	assert cycle.getAttr('conditionFrame') == [opcodes.VARIABLE(name='True')]
	assert cycle.getAttr('code') == [
		opcodes.CALL_FUNCTION(dst='__IV11', function='print'),
		opcodes.VARIABLE(name='__IV11')
	]


def test_whileWithSimpleStringPrint(parse):
	cycle = parse('while True: print("1")').one()

	assert cycle.getAttr('__class__').equal(While)
	assert cycle.getAttr('conditionFrame') == [opcodes.VARIABLE(name='True')]
	assert cycle.getAttr('code') == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV11', function='String', typeb='(', args=['1'], kwargs={}
		),
		opcodes.CALL_FUNCTION(dst='__IV12', function='print', typeb='(', args=['__IV11'], kwargs={}),
		opcodes.VARIABLE(name='__IV12')
	]


def test_whileWithFullCodeBlock(parse):
	cycle = parse('while True:\n	print(1)\n	print(2)').one()

	assert cycle.getAttr('__class__').equal(While)
	assert cycle.getAttr('conditionFrame') == [opcodes.VARIABLE(name='True')]
	assert cycle.getAttr('code') == [
		opcodes.CALL_FUNCTION_STATIC(dst='__IV11', function='Number', typeb='(', args=['1'], kwargs={}),
		opcodes.CALL_FUNCTION(dst='__IV12', function='print', typeb='(', args=['__IV11'], kwargs={}),
		opcodes.VARIABLE(name='__IV12'),
		opcodes.CALL_FUNCTION_STATIC(dst='__IV13', function='Number', typeb='(', args=['2'], kwargs={}),
		opcodes.CALL_FUNCTION(dst='__IV14', function='print', typeb='(', args=['__IV13'], kwargs={}),
		opcodes.VARIABLE(name='__IV14'),
	]


def test_setVariable(parse):
	code = parse('a = 1')
	assert code == [
		opcodes.CALL_FUNCTION_STATIC(
			dst='__IV11', function='Number', typeb='(', args=['1'], kwargs={}
		),
		opcodes.SET_VARIABLE(dst='a', src='__IV11')
	]
