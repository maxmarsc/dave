# import unittest
from unittest import TestCase, TestLoader, TextTestRunner, TextTestResult, TestSuite
import sys
import os
from pathlib import Path

TEST_DIR = Path(__file__).parent
try:
    FILTER: str = os.environ["FILTER"]
except:
    FILTER = None


def filter_test_suite(suite: TestSuite, filter: str):
    """Recursively filter a TestSuite to find tests matching filter."""
    filtered_suite = TestSuite()

    for item in suite:
        if isinstance(item, TestSuite):
            # Recursively filter sub-suites
            matches = filter_test_suite(item, filter)
            if matches.countTestCases() > 0:
                filtered_suite.addTest(matches)
        elif isinstance(item, TestCase):
            # Check if the filter string is inside the test ID
            # Test ID format: package.module.Class.method
            if filter in item.id():
                filtered_suite.addTest(item)

    return filtered_suite


class CustomTextTestResult(TextTestResult):
    def startTest(self, test):
        super(TextTestResult, self).startTest(test)
        if self.showAll:
            self.stream.write(self.getDescription(test))
            self.stream.write(" ... \n")
            self.stream.flush()
            self._newline = True


def run() -> TextTestResult:
    loader = TestLoader()

    # This ensures all paths/imports are handled correctly by the loader.
    full_suite = loader.discover(start_dir=TEST_DIR)

    # Filter (optional)
    if FILTER:
        print(f"WARNING: Filtering tests with pattern: '{FILTER}'")
        test_suite = filter_test_suite(full_suite, FILTER)
    else:
        test_suite = full_suite

    runner = TextTestRunner(
        verbosity=2, stream=sys.stdout, resultclass=CustomTextTestResult
    )
    return runner.run(test_suite)
