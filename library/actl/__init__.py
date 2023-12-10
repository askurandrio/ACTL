import signal
import sys
import logging
import traceback

from .utils import *
from . import objects
from . import opcodes
from .Buffer import Buffer
from .parser import Parser
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


if 'DEBUG_TIMER' in os.environ:

	def debug(_, frame):
		print(''.join(traceback.format_stack(frame)))
		breakpoint()  # pylint: disable=forgotten-debug-statement

	signal.signal(signal.SIGALRM, debug)

	DEBUG_TIMER = int(os.environ['DEBUG_TIMER'])
	if DEBUG_TIMER > 0:
		signal.alarm(DEBUG_TIMER)


if 'ACTL_ENABLE_TRACEMALLOC' in os.environ:
	import tracemalloc

	tracemalloc.start()


_makeLogger()
