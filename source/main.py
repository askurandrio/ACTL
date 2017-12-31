
import os
import sys
import copy

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

from actl import Project


def main(mainf):
   project = Project(mainf=mainf)


main(*sys.argv[1:])

