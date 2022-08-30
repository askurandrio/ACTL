import fcntl
import os
import subprocess
import time

import pytest

from actl import DIR_LIBRARY


class _Run:
	_actlBinary = os.path.join(os.path.dirname(DIR_LIBRARY), 'actl')

	def __call__(self, *args):
		self.process = subprocess.Popen(  # pylint: disable=consider-using-with
			args=[self._actlBinary, *args],
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
		)

		fcntl.fcntl(self.process.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

	def writeLine(self, line):
		self.process.stdin.write(f'{line}\n'.encode())
		self.process.stdin.flush()

	def reader(self):
		line = ''
		startTime = time.time()

		while True:
			assert (time.time() - startTime) < 5, f'Timeout exceeded, {line=}'

			char = self.process.stdout.read(1)
			if not char:
				assert self.process.poll() is None, self.process.returncode
				time.sleep(0.1)
				continue

			line += char.decode()
			yield line

	def readLine(self):
		for line in self.reader():
			if line.endswith('\n'):
				return line

		raise RuntimeError('No line found')

	def readTemplate(self, template):
		for line in self.reader():
			if line == template:
				break


@pytest.fixture
def run(cleanupOnSuccess, cleanupOnFailure):
	run_ = _Run()

	@cleanupOnFailure
	def _cleanupRunOnFailure():
		run_.process.kill()

	@cleanupOnSuccess
	def _cleanupRunOnSuccess():
		run_.process.stdin.close()
		run_.process.wait(timeout=5)
		assert run_.process.returncode == 0, run_.process.returncode

		output = run_.process.stdout.read()
		assert not output, output

	return run_
