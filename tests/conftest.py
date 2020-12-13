import traceback
import signal

import pytest


@pytest.fixture
def debugStuck():
	def debug(_, frame):
		print(traceback.format_stack(frame))
		breakpoint()

	signal.signal(signal.SIGALRM, debug)
	signal.alarm(20)
