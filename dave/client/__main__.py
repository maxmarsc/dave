import sys
import os
from multiprocessing.connection import Connection


"""
This runfile expect a pipe file descriptor to communicate with the debugger server

It will starts the GUI of dave, and automatically shutdown if the connection is closed
"""

# Attempt to create the connection
try:
    fd = int(sys.argv[1])

    # Check if the file descriptor is valid
    if not os.isatty(fd) and fd > 0:  # os.isatty() will check if it's a valid open FD
        gui_con = Connection(fd)
    else:
        raise ValueError("Invalid file descriptor")

except (OSError, ValueError) as e:
    print(f"Error creating connection from file descriptor: {e}")
    sys.exit(1)

try:
    from . import DaveGUI
except ImportError as e:
    import os
    import logging

    LOGLEVEL = os.environ.get("DAVE_LOGLEVEL", "INFO").upper()
    logging.critical(
        "Tried to load GUI from incompatible interpreter\n"
        f"sys.executable : {sys.executable}\n"
        f"sys.path : {sys.path}\n"
    )
    raise e

# gui_con = Connection(int(sys.argv[1]))
# gui = DaveGUI(gui_con)
# gui.run()
DaveGUI.start(gui_con)
