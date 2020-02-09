# pylint: disable=redefined-outer-name

import os
import subprocess

import pytest

import actl


@pytest.fixture
def run():
	root = os.path.dirname(os.path.dirname(actl.__path__[0]))
	actlBinPath = os.path.join(root, 'actl')

	def run_(args, inp):
		process = subprocess.run(
			(actlBinPath, *args),
			input='\n'.join(inp),
			stdout=subprocess.PIPE,
			check=True
		)
		return process.stdout.decode().split('\n')

	return run_


def test_simpleRepl(run):
	assert run((), ()) == ['>>> ']


def test_expliciSetProjectF(run):
	assert run(('--projectf', 'repl'), ()) == ['>>> ']
