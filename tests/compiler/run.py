
import os
import unittest
import tempfile
import warnings
import itertools
import subprocess


WORK_DIR = os.path.dirname(os.path.abspath(__file__))
CASES_DIR = os.path.join(WORK_DIR, 'cases')
DIR_SOURCE = os.path.join(os.path.dirname(os.path.dirname(WORK_DIR)), 'source')


class TempFile:
	def __init__(self):
		self.name = tempfile.NamedTemporaryFile(delete=False).name

	def __del__(self):
		os.remove(self.name)


def assertEqFile(first, second):
	nlines, ffirst, fsecond = itertools.count(0), open(first), open(second)
	result = True
	while True:
		nline, fline, sline = next(nlines), next(ffirst, ''), next(fsecond, '') 
		if (not fline) and (not sline):
			if result:
				return True
			else:
				print(first, open(first).read(), sep='\n')
				print(second, open(second).read(), sep='\n')
				assert False, f"<{first}> != <{second}>"
			return result
		if fline != sline:
			result = False
			print(nline, ': "', fline[:-1], '" != "', sline[:-1], '"')


class TestCompiler(unittest.TestCase):
	def compile(self, filename):
		projectf = os.path.join(CASES_DIR, 'project.yaml')
		filename = os.path.join(CASES_DIR, filename)
		tmpl_filename = os.path.splitext(filename)[0] + '.a.cout'
		process = subprocess.Popen(f'python {DIR_SOURCE}/actl {projectf} {filename}')
		process.wait()
		assert process.returncode == 0
		assertEqFile(self.out_fname, tmpl_filename)

	@staticmethod
	def build():
		for filename in sorted(os.listdir(CASES_DIR)):
			if os.path.splitext(filename)[1] != '.a':
				continue

			def test_func(self, filename=filename):
				self.compile(filename)
			test_name = f'test_{os.path.splitext(filename)[0]}'
			setattr(TestCompiler, test_name, test_func)


TestCompiler.build()


if __name__ == '__main__':
	warnings.simplefilter("ignore")
	warnings.simplefilter("ignore")
	unittest.main()
