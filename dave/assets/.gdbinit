# --- DAVE BEGIN ---
python
# Update GDB's Python paths with the `sys.path` values of the local
# This is needed to find the common and server parts of dave

# Convert GDB to interpret in Python
import os, subprocess, sys

# Execute a Python using the user's shell and pull out the sys.path (for site-packages)
paths = (
    subprocess.check_output(
        'python -c "import os,sys;print(os.linesep.join(sys.path).strip())"', shell=True
    )
    .decode("utf-8")
    .split()
)
# Extend GDB's Python's search path
sys.path.extend(paths)
# sys.path = paths + sys.path
try:
    import dave.server.debuggers.gdb
except ModuleNotFoundError as e:
    import os
    import logging

    LOGLEVEL = os.environ.get("DAVE_LOGLEVEL", "INFO").upper()
    logging.basicConfig(level=LOGLEVEL, format="%(levelname)s: %(message)s")
    logging.warning("[dave] module not found. Commands will not be available")
    logging.debug(f"failed with {e}")
    logging.debug(f"sys.path : {sys.path}")
end
# --- DAVE END ---
