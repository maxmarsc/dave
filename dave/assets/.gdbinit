# --- DAVE BEGIN ---
python
# Update GDB's Python paths with the `sys.path` values of the local
# This is needed to find the common and server parts of dave

import os, subprocess, sys, site
from pathlib import Path

try:
    DAVE_VENV_PATH = Path(os.environ["DAVE_VENV_FOLDER"]) / "bin/activate"
except KeyError:
    DAVE_VENV_PATH = Path.home() / ".dave/venv/bin/activate"

# Execute a Python using the user's shell and pull out the sys.path (for site-packages)
if DAVE_VENV_PATH.is_file():
    paths = (
        subprocess.check_output(
            '. {};python -c "import os,sys;print(os.linesep.join(sys.path).strip())"'.format(
                DAVE_VENV_PATH
            ),
            shell=True,
        )
        .decode("utf-8")
        .split()
    )
    # Delete duplicates and update the search list with dave venv
    for path in paths:
        if path not in sys.path:
            site.addsitedir(path)
try:
    import dave.server.debuggers.gdb_
except ModuleNotFoundError as e:
    import os
    import logging
    import gdb

    LOGLEVEL = os.environ.get("DAVE_LOGLEVEL", "INFO").upper()
    gdb.write("WARNING : [dave] module not found. Commands will not be available\n")
    if LOGLEVEL == "DEBUG":
        gdb.write(f"DEBUG : failed with {e}\n")
        gdb.write(f"DEBUG : sys.path : {sys.path}\n")
end
# --- DAVE END ---
