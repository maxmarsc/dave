# import unittest
from unittest import TestLoader, TextTestRunner, TextTestResult
import sys
from pathlib import Path

TEST_DIR = Path(__file__).parent


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
    test_suite = loader.discover(start_dir=TEST_DIR)

    runner = TextTestRunner(
        verbosity=2, stream=sys.stdout, resultclass=CustomTextTestResult
    )
    return runner.run(test_suite)
