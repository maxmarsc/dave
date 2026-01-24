from .test_case import TestCaseBase
from .debugger import DebuggerAbstraction, CommandError

import os
from pathlib import Path

try:
    C_CPP_BUILD_DIR = Path(os.environ["C_CPP_BUILD_DIR"])
except KeyError:
    raise RuntimeError("C_CPP_BUILD_DIR is not set")

# try:
#     RUST_BUILD_DIR = Path(os.environ["RUST_BUILD_DIR"])
# except KeyError:
#     raise RuntimeError("RUST_BUILD_DIR is not set")
