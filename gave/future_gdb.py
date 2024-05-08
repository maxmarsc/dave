import signal
import threading
from contextlib import contextmanager

# This was imported from gdb-14


@contextmanager
def blocked_signals():
    """A helper function that blocks and unblocks signals."""
    if not hasattr(signal, "pthread_sigmask"):
        yield
        return

    to_block = {signal.SIGCHLD, signal.SIGINT, signal.SIGALRM, signal.SIGWINCH}
    old_mask = signal.pthread_sigmask(signal.SIG_BLOCK, to_block)
    try:
        yield None
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)


class Thread(threading.Thread):
    """A GDB-specific wrapper around threading.Thread

    This wrapper ensures that the new thread blocks any signals that
    must be delivered on GDB's main thread."""

    def start(self):
        # GDB requires that these be delivered to the main thread.  We
        # do this here to avoid any possible race with the creation of
        # the new thread.  The thread mask is inherited by new
        # threads.
        with blocked_signals():
            super().start()
