from .test_case import TestCaseBase
from .debugger import DebuggerAbstraction, CommandError

import os
from pathlib import Path

try:
    C_CPP_BUILD_DIR = Path(os.environ["C_CPP_BUILD_DIR"])
except KeyError:
    C_CPP_BUILD_DIR = Path("MISSING_C_CPP_BUILD_DIR")

try:
    RUST_BUILD_DIR = Path(os.environ["RUST_BUILD_DIR"])
except KeyError:
    RUST_BUILD_DIR = Path("MISSING_RUST_BUILD_DIR")
