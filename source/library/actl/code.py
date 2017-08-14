import sys

import pyparsing


ALPHAS = ''.join(filter(str.isalpha, map(chr, range(sys.maxunicode + 1))))


class Name:
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"Name('{self.name}')"
    
    @classmethod
    def get_parser(cls):
        word = pyparsing.Word(ALPHAS + '_', ALPHAS + '_'+ pyparsing.nums)
        word.setParseAction(lambda tokens: cls(tokens[0]))
        return word


class Number:
    def __init__(self, number):
        self.number = number
    
    def __repr__(self):
        return f"Number({self.number})"
    
    @classmethod
    def get_parser(cls):
        word = pyparsing.Word(pyparsing.nums, pyparsing.nums + '.')
        word.setParseAction(lambda tokens: cls(tokens[0]))
        return word


class Operator:
    def __init__(self, operator):
        self.operator = operator
    
    def __repr__(self):
        return f"Operator({self.operator})"
    
    @classmethod
    def get_parser(cls):
        word = pyparsing.Word('+-=*/')
        word.setParseAction(lambda tokens: cls(tokens[0]))
        return word


class OpenCodeBlock:
    pass


class Parser:
    def __init__(self, buff):
        self.buff = buff
        self.rules = self.__get_rules()

    def __iter__(self):
        while self.buff:
            is_find = False
            for rule in self.rules:
                for result, start, end in rule.scanString(self.buff):
                    if start == 0:
                        is_find = True
                        self.buff = self.buff[end:]
                        yield result
                    break
            if not is_find:
                raise RuntimeError(self.buff)

    def __get_rules(self):
        rules = []
        rules.append(Operator.get_parser())
        rules.append(Name.get_parser())
        rules.append(Number.get_parser())
        return rules
