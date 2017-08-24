import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

from actl import Code, Parser
from cpp import Translator


def main(input_filename, output_filename):
    parser = Parser(open(input_filename, encoding='utf-8').read())
    code = Code(parser)
    for inst in code.compile():
        print(inst)
    print(Translator(code).translate())


main(*sys.argv[1:])