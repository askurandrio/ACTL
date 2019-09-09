import actl
import actl_types
from actl import opcodes


class Translator:
    def __init__(self, code):
        self.code = code

    def translate(self, ident=0, add_main=True):
        s = ''.join(self.__translate(ident))
        if add_main:
            s += 'int main() {\n    return 0;\n} \n\n'
        return s

    def __translate(self, ident):
        for opcode in self.code:
            if isinstance(opcode, actl.Code):
                yield (' ' * ident) + '{\n'
                yield from self.__class__(opcode).translate(ident=ident+4, add_main=False)
                yield (' ' * ident) + '}\n'
            else:
                yield self.get_cpp_code(opcode)

    @classmethod
    def get_cpp_code(cls, opcode):
        if isinstance(opcode, opcodes.DECLARE):
            type = cls.get_cpp_code(opcode.type)
            name = cls.get_cpp_code(opcode.name)
            return f'{type} {name};\n'
        elif isinstance(opcode, opcodes.SET):
            name = cls.get_cpp_code(opcode.name)
            value = cls.get_cpp_code(opcode.value)
            return f'{name} = {value};\n'
        elif isinstance(opcode, opcodes.Variable):
            return str(opcode.name)
        elif isinstance(opcode, int) or isinstance(opcode, float):
            return str(opcode)
        else:
            raise RuntimeError(opcode)
