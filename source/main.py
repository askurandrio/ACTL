
import os
import sys
import copy

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

from actl import Project


def main(input_filename):
   project = Project(main=open(input_filename, encoding='utf-8').read())


main(*sys.argv[1:])

