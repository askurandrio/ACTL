
import sys

from actl import Project


def main(mainf, projectf):
	project = Project(projectf=projectf)
	project.compile(filename=mainf)


main(*sys.argv[1:])

