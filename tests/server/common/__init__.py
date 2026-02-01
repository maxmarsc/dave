from .test_case import TestCaseBase
from .debugger import DebuggerAbstraction, CommandError

import os
from pathlib import Path

try:
    C_CPP_BUILD_DIR: Path = Path(os.environ["C_CPP_BUILD_DIR"])
except KeyError:
    C_CPP_BUILD_DIR = None

try:
    RUST_BUILD_DIR: Path = Path(os.environ["RUST_BUILD_DIR"])
except KeyError:
    RUST_BUILD_DIR = None
