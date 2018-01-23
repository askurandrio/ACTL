
import os
import subprocess


WORK_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_LIBRARY = os.path.join(os.path.dirname(WORK_DIR), 'source', 'library')


def set_pythonpath():
	if DIR_LIBRARY != os.environ.get('PYTHONPATH'):
		os.environ['PYTHONPATH'] = DIR_LIBRARY 


def test_engine():
	process = subprocess.Popen(f'python {WORK_DIR}/engine/run.py', env=os.environ)
	process.wait()
	assert process.returncode == 0


def test_compiler():
	process = subprocess.Popen(f'python {WORK_DIR}/compiler/run.py')
	process.wait()
	assert process.returncode == 0


def main():
	set_pythonpath()
	test_engine()
	test_compiler()


if __name__ == '__main__':
	main()
