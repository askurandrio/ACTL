
import sys
import logging

from .code import *
from .project.Project import Project


def __make_loggers():
	logger = logging.getLogger('actl')
	formatter = logging.Formatter('%(process)d %(asctime)s: [%(levelname)s] %(message)s')

	stdout = logging.StreamHandler(sys.stdout)
	stdout.setFormatter(formatter)
	logger.addHandler(stdout)


__make_loggers()
