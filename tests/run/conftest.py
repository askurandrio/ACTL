import fcntl
import os
import subprocess
import sys
import time
import shlex

import pytest

from actl import DIR_LIBRARY


class _Run:
	_actlBinary = os.path.join(os.path.dirname(DIR_LIBRARY), 'actl')
	_readerTimeout = int(os.environ.get('ACTL_READER_TIMEOUT', '60'))

	def __call__(self, *args, **kwargs):
		self.process = subprocess.Popen(  # pylint: disable=consider-using-with
			args=[self._actlBinary, *args],
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			**kwargs,
		)

		for file in (self.process.stdout, self.process.stderr):
			fcntl.fcntl(file.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

		self._stderr = ''

	def readStdErr(self, count=None):
		chars = self.process.stderr.read(count)
		if chars:
			self._stderr += chars.decode()
		return self._stderr

	def writeLine(self, line):
		self.process.stdin.write(f'{line}\n'.encode())
		self.process.stdin.flush()

	def reader(self):
		line = ''
		startTime = time.time()

		while True:
			assert (
				time.time() - startTime
			) < self._readerTimeout, f'Timeout exceeded, {line=}'

			char = self.process.stdout.read(1)
			if not char:
				assert self.process.poll() is None, self.process.returncode
				self.readStdErr(1)
				if self._stderr:
					raise RuntimeError('stderr is not empty')
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
			if ('\n' in line) and (template[: len(line)] != line):
				raise RuntimeError(
					f'readTemplate already can not be successful. template<"{template}"> != line<"{line}">'
				)

			if line == template:
				break


@pytest.fixture
def run(cleanupOnSuccess, cleanupOnFailure):
	run_ = _Run()

	@cleanupOnFailure
	def _cleanupRunOnFailure():
		run_.process.stdin.close()
		run_.process.kill()
		run_.process.wait(timeout=1)

		print(
			f"'{shlex.join(run_.process.args)}' cleanup on failure with returncode {run_.process.returncode}",
			file=sys.stderr,
		)
		print(run_.readStdErr(), file=sys.stderr)

	@cleanupOnSuccess
	def _cleanupRunOnSuccess():
		run_.process.stdin.close()
		run_.process.wait(timeout=5)
		assert run_.process.returncode == 0, run_.process.returncode

		output = run_.process.stdout.read()
		assert not output, output

	return run_
