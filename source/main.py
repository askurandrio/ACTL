import sys


def main(input_filename, bytecode_filename, output_filename):
    code = Code.parse(input_filename)
    code.write(bytecode_filename)
    code = Code.read_bytecode(bytecode_filename)
    cpp_code = code.translate()
    cpp_code.write(output_filename)


main(sys.argv[1:3]*)