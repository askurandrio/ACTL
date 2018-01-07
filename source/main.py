
import sys

from actl import Project


def main(mainf):
   project = Project(mainf=mainf)


main(*sys.argv[1:])

