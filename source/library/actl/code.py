import sys

import pyparsing


ALPHAS = ''.join(filter(str.isalpha, map(chr, range(sys.maxunicode + 1))))


class Parser:
    def __init__(self, chars):
        self.chars = chars
        self.parser = pyparsing.Word(ALPHAS + '_')

    def __iter__(self):
        for result in self.parser.parseString(self.chars, parseAll=True):
            yield result
