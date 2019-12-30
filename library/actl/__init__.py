
import sys
import logging

from . import objects
from .Buffer import Buffer
from .Parser import Parser
from .Project import Project
from .Scope import Scope


def _make_logger():
	logger = logging.getLogger('actl')
	formatter = logging.Formatter('%(process)d %(asctime)s: [%(levelname)s] %(message)s')

	stdout = logging.StreamHandler(sys.stdout)
	stdout.setFormatter(formatter)
	logger.addHandler(stdout)


_make_logger()
