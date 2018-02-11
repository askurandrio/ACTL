
from actl.parser import tokens
from .Function import Function

abuiltins = {tokens.VARIABLE('def'): Function}
