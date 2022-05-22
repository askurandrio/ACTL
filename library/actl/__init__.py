import sys
import logging

from .utils import *
from . import objects
from . import opcodes
from .Buffer import Buffer
from .Parser import Parser
from .project import *
from .Scope import Scope


def _makeLogger():
	logger = logging.getLogger('actl')
	formatter = logging.Formatter(
		'%(process)d %(asctime)s: [%(levelname)s] %(message)s'
	)

	stdout = logging.StreamHandler(sys.stdout)
	stdout.setFormatter(formatter)
	logger.addHandler(stdout)


_makeLogger()
