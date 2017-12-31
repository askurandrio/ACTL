import sys

import pyparsing

from ..code.opcodes.AnyOpCode import AnyOpCode


class Word(AnyOpCode):
    symbols = ''.join(filter(str.isalpha, map(chr, range(sys.maxunicode + 1)))) + '_' + \
                pyparsing.nums

    def __init__(self, word):
        self.word = word
    
    def __eq__(self, item):
        if super().__eq__(item):
            return self.word == item.word
        return False

    def __repr__(self):
        return f"Word('{self.word}')"

    @classmethod
    def get_parsers(cls):
        word = pyparsing.Word(cls.symbols)
        word.setParseAction(lambda tokens: cls(tokens[0]))
        yield word


class Operator(AnyOpCode):
    symbols = ':.,+-=*/()<>![]{}=!@;'

    def __init__(self, operator):
        if operator == '\n':
            operator = 'line_end'
        self.operator = operator

    def __eq__(self, item):
        if super().__eq__(item):
            return self.operator == item.operator
        return False
    
    def __repr__(self):
        return f"Operator({self.operator})"
    
    @classmethod
    def get_parsers(cls):
        parser = pyparsing.LineEnd()
        parser.setParseAction(lambda _: cls('line_end'))
        yield parser

        parser = pyparsing.Word(cls.symbols)
        parser.setParseAction(lambda tokens: cls(tokens[0]))
        yield parser
