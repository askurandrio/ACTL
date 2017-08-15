import sys

sys.path.append('./library')

from actl import Code, Parser


def main(input_filename):
    parser = Parser(open(input_filename, encoding='utf-8').read())
    code = Code(parser)
    for inst in code.compile():
        print(inst)


main(*sys.argv[1:])