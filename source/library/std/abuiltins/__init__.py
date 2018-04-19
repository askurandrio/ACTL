
from actl.tokenizer import tokens
from .Function import Function

abuiltins = {tokens.VARIABLE('def'): Function}
