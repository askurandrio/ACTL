
import sys

from actl import Project


def main(filename):
	project = Project()
	project.compile(filename=filename)


main(*sys.argv[1:])

