import sys

from code import Parser


def main(input_filename):
    code = Parser(file=input_filename).parse()
    print(code)

main(*sys.argv[1:])