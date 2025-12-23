import subprocess
import sys
import os
import site
from pathlib import Path
import lldb

os.environ["DAVE_LOGLEVEL"] = "CRITICAL"

tests_root = Path(__file__).resolve().parent.parent
if tests_root not in sys.path:
    site.addsitedir(tests_root)

from lldb_testing import LldbTestCase


def load_dave():
    init_file = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "dave"
        / "assets"
        / "lldb_init.py"
    )
    assert init_file.is_file()

    debugger: lldb.SBDebugger = lldb.debugger
    ci: lldb.SBCommandInterpreter = debugger.GetCommandInterpreter()
    res = lldb.SBCommandReturnObject()
    ci.HandleCommand(f"command script import {init_file}", res)

    if not res.Succeeded():
        sys.exit(1)


def main():
    # First, ensure dave loads correctly
    load_dave()

    # Then bind TEST_CASE_BASE to GdbTestCase
    LldbTestCase.declare_as_base_test_class()

    # Then import and run the tests
    from test_suite import run

    result = run()
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)


def __lldb_init_module(debugger, internal_dict):
    try:
        main()
    except Exception as e:
        import traceback

        traceback.print_tb(e.__traceback__)
        print(f"ERROR: Test suite failed to run: {e}\n", file=sys.stderr)
        sys.exit(1)
