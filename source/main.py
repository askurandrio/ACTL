
import sys

from actl import Project


def main(mainf, projectf):
	project = Project(mainf=mainf, projectf=projectf)
	project.compile()


main(*sys.argv[1:])

