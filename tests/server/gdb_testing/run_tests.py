import subprocess
import sys
import os
import site
from pathlib import Path
import gdb  # type: ignore

tests_root = Path(__file__).resolve().parent.parent
if tests_root not in sys.path:
    site.addsitedir(tests_root)

from gdb_testing import GdbTestCase


def load_dave():
    venv_path = Path(os.environ["DAVE_VENV_FOLDER"]) / "bin/activate"
    paths = (
        subprocess.check_output(
            '. {};python -c "import os,sys;print(os.linesep.join(sys.path).strip())"'.format(
                venv_path
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

    import dave.server.debuggers.gdb_


def main():
    # First, ensure dave loads correctly
    load_dave()

    # Then bind TEST_CASE_BASE to GdbTestCase
    GdbTestCase.declare_as_base_test_class()
    # global TEST_CASE_BASE
    # TEST_CASE_BASE = GdbTestCase
    # gdb.execute("set pagination off")
    # gdb.execute("set logging file /dev/null", to_string=True)
    # gdb.execute("set logging redirect on", to_string=True)
    # gdb.execute("set logging enabled on")

    # # Suppress the message printed when a new thread is started
    # gdb.execute("set print thread-events off")

    # Then import and run the tests
    from test_suite import run

    result = run()
    if result.wasSuccessful():
        gdb.execute("quit 0")
    else:
        gdb.execute("quit 1")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback

        traceback.print_tb(e.__traceback__)
        gdb.execute("set logging enabled off")
        gdb.write(f"ERROR: Test suite failed to run: {e}\n")
        gdb.execute("quit 1", to_string=True)
