# pylint: disable=redefined-outer-name

import os
import subprocess

import json
import pytest

import actl


@pytest.fixture
def run():
	root = os.path.dirname(os.path.dirname(actl.__path__[0]))
	actlBinPath = os.path.join(root, 'actl')

	def run_(args, inp=None):
		if inp is not None:
			inp = inp.encode()
		print(' '.join((actlBinPath, *args)))
		process = subprocess.run(
			(actlBinPath, *args),
			input=inp,
			stdout=subprocess.PIPE,
			check=True
		)
		return process.stdout.decode().split('\n')

	return run_


def test_simpleRepl(run):
	assert run(()) == ['>>> ']


def test_expliciSetProjectF(run):
	assert run(('--projectf', 'repl')) == ['>>> ']


def test_setExtraSource(run):
	extraSource = [
		{
			'py-key': {
				'name': 'scope',
				'code': '''
				import actl

				scope = this['std', 'scope']
				scope['print'] = actl.objects.PyToA.call(lambda inp: print(f'mocked: {inp}'))
				
				return scope
				'''
			}
		}
	]

	assert run(('--source', json.dumps(extraSource)), 'print(1)') == ['>>> ', 'mocked: 1', '>>> ']
