
import os
import subprocess


WORK_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_SOURCE = os.path.join(os.path.dirname(os.path.dirname(WORK_DIR)), 'source')


def main():
	for filename in os.listdir(WORK_DIR):
		if os.path.splitext(filename)[1] == '.a':
			filename = os.path.join(WORK_DIR, filename)
			process = subprocess.Popen(f'python {DIR_SOURCE}/main.py {filename}')
			process.wait()
			assert process.returncode == 0


if __name__ == '__main__':
	main()
