import sys

import pyparsing

from ..opcodes.AnyOpCode import AnyOpCode


class Word(AnyOpCode):
    symbols = ''.join(filter(str.isalpha, map(chr, range(sys.maxunicode + 1))))

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
        word = pyparsing.Word(cls.symbols + '_', cls.symbols + '_'+ pyparsing.nums)
        word.setParseAction(lambda tokens: cls(tokens[0]))
        yield word


class Number(AnyOpCode):
    def __init__(self, number):
        self.number = number
    
    def __eq__(self, item):
        if super().__eq__(item):
            return self.number == item.number
        return False

    def __repr__(self):
        return f"AnyOpCode.{self.__class__.__name__}({self.number})"
    
    @classmethod
    def get_parsers(cls):
        parser = pyparsing.Word(pyparsing.nums, pyparsing.nums + '.')
        parser.setParseAction(lambda tokens: cls(float(tokens[0])))
        yield parser


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
