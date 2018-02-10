
import os
import tempfile
import subprocess


WORK_DIR = os.path.dirname(os.path.abspath(__file__))
CASES_DIR = os.path.join(WORK_DIR, 'cases')
DIR_SOURCE = os.path.join(os.path.dirname(os.path.dirname(WORK_DIR)), 'source')


class TempFile:
	def __init__(self):
		self.name = tempfile.NamedTemporaryFile(delete=False).name

	def __del__(self):
		os.remove(self.name)


def main():
	out_fname = TempFile().name
	os.environ['out_fname'] = out_fname
	pfname = os.path.join(CASES_DIR, 'test_compiler.yaml')
	for filename in os.listdir(CASES_DIR):
		if os.path.splitext(filename)[1] == '.a':
			filename = os.path.join(CASES_DIR, filename)
			tmpl_filename = os.path.splitext(filename)[0] + '.a.cout'
			process = subprocess.Popen(f'python {DIR_SOURCE}/main.py {filename} {pfname}')
			process.wait()
			assert process.returncode == 0
			assert open(out_fname).read() == open(tmpl_filename).read()

if __name__ == '__main__':
	main()
