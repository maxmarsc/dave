# import unittest
from unittest import TestLoader, TextTestRunner, TextTestResult
import sys
from pathlib import Path

TEST_DIR = Path(__file__).parent


def run() -> TextTestResult:
    loader = TestLoader()
    test_suite = loader.discover(start_dir=TEST_DIR)

    runner = TextTestRunner(verbosity=2, stream=sys.stdout)
    return runner.run(test_suite)
