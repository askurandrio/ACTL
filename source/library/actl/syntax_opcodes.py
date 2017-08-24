import sys

import pyparsing

from .opcodes import AnyVirtualOpCode


OPERATORS = '.+-=*/,()[]{}=!@'
ALPHAS = ''.join(filter(str.isalpha, map(chr, range(sys.maxunicode + 1))))


class AnySyntaxCode(AnyVirtualOpCode):
    def __eq__(self, item):
        return isinstance(item, self.__class__)


class Word(AnySyntaxCode):
    def __init__(self, word):
        self.word = word
    
    def __eq__(self, item):
        if AnySyntaxCode.__eq__(self, item):
            return self.word == item.word
        return False

    def __repr__(self):
        return f"AnySyntaxCode.{self.__class__.__name__}('{self.word}')"

    @classmethod
    def get_parser(cls):
        word = pyparsing.Word(ALPHAS + '_', ALPHAS + '_'+ pyparsing.nums)
        word.setParseAction(lambda tokens: cls(tokens[0]))
        return word


class Number(AnySyntaxCode):
    def __init__(self, number):
        self.number = number
    
    def __eq__(self, item):
        if AnySyntaxCode.__eq__(self, item):
            return self.number == item.number
        return False

    def __repr__(self):
        return f"AnySyntaxCode.{self.__class__.__name__}({self.number})"
    
    @classmethod
    def get_parser(cls):
        word = pyparsing.Word(pyparsing.nums, pyparsing.nums + '.')
        word.setParseAction(lambda tokens: cls(float(tokens[0])))
        return word


class Operator(AnySyntaxCode):
    def __init__(self, operator):
        self.operator = operator

    def __eq__(self, item):
        if AnySyntaxCode.__eq__(self, item):
            return self.operator == item.operator
        return False
    
    def __repr__(self):
        return f"AnySyntaxCode.{self.__class__.__name__}({self.operator})"
    
    @classmethod
    def get_parsers(cls):
        word = pyparsing.LineEnd().suppress()
        word.setParseAction(lambda _: cls.NEXT_LINE_CODE)
        yield word

        word = pyparsing.Word(':')
        word.setParseAction(lambda _: cls.OPEN_CODE)
        yield word

        word = pyparsing.Word(OPERATORS)
        word.setParseAction(lambda tokens: cls(tokens[0]))
        yield word


Operator.EMPTY = Operator(None)
Operator.OPEN_CODE = Operator('open_code')
Operator.CLOSE_CODE =  Operator('close_code')
Operator.NEXT_LINE_CODE =  Operator('next_line_code')
