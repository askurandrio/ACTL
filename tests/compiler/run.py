
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
	@classmethod 
	def setUpClass(cls):
		warnings.simplefilter("ignore")

		cls.pfname = os.path.join(CASES_DIR, 'test_compiler.yaml')
		cls.out_fname = TempFile().name
		os.environ['out_fname'] = cls.out_fname

	def test_steps(self):
		warnings.simplefilter("ignore")

		for filename in sorted(os.listdir(CASES_DIR)):
			if os.path.splitext(filename)[1] == '.a':
				filename = os.path.join(CASES_DIR, filename)
				tmpl_filename = os.path.splitext(filename)[0] + '.a.cout'
				process = subprocess.Popen(f'python {DIR_SOURCE}/main.py {self.pfname} {filename}')
				process.wait()
				try:
					assert process.returncode == 0
					assertEqFile(self.out_fname, tmpl_filename)
				except Exception as ex:
					self.fail("{} failed ({}: {})".format(filename, type(ex), ex))


unittest.main()
