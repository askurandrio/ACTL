import sys

sys.path.append('./library')

from actl.code import Parser


def main(input_filename):
    code = Parser(open(input_filename, encoding='utf-8').read())
    for inst in code:
        print(inst)


main(*sys.argv[1:])