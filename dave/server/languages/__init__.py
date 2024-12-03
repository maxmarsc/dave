import dave.common.server_type as st

# First import vanilla dave support
if st.SERVER_TYPE in (st.ServerType.GDB, st.ServerType.LLDB):
    from .c_cpp import *
elif st.SERVER_TYPE == st.ServerType.PYTHON:
    from .python import *
else:
    raise RuntimeError(f"Unsupported server type {st.SERVER_TYPE}")

from dave.common.logger import Logger

Logger().debug(f"Detected debugger : {st.SERVER_TYPE}")

# Then custom container support
import os, sys
from pathlib import Path
import importlib.util

if "DAVE_VENV_FOLDER" in os.environ:
    import dave

    custom_module_path = (
        Path(dave.__file__).parent.parent / "examples/custom/__init__.py"
    )
else:
    custom_module_path = Path.home() / ".dave/custom/__init__.py"

if not custom_module_path.is_file():
    Logger().debug(
        f"Custom containers init file not found : {custom_module_path}, skipping"
    )
else:
    Logger().debug(f"Trying to import custom containers from {custom_module_path}")

    spec = importlib.util.spec_from_file_location("custom", custom_module_path)
    custom_m = importlib.util.module_from_spec(spec)
    sys.modules["custom"] = custom_m
    spec.loader.exec_module(custom_m)
