
import sys

from actl import Project


def main(mainf):
	project = Project()
	project.compile(filename=mainf)


main(*sys.argv[1:])

