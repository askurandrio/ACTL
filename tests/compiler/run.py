
import os
import subprocess


WORK_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_LIBRARY = os.path.join(os.path.dirname(os.path.dirname(WORK_DIR)), 'source', 'library')


def main():
	for filename in os.listdir(WORK_DIR):
		if os.path.splitext('filename')[0] == '.a':
			filename = os.path.join(WORK_DIR, filename)
			process = subprocess.Popen(f'python {WORK_DIR}/main.py {filename}')
			process.wait()
			assert process.returncode == 0


if __name__ == '__main__':
	main()
