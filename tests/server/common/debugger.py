from abc import ABC, abstractmethod
from contextlib import contextmanager
import os
from typing import List, Deque, Tuple, Union
from itertools import islice
from collections import deque


@contextmanager
def stdout_silence():
    # Save a copy of the actual terminal output (FD 1)
    stdout_fd = 1
    saved_stdout_fd = os.dup(stdout_fd)

    try:
        # Redirect FD 1 to /dev/null
        # This affects the ENTIRE process, including GDB's C code
        with open(os.devnull, "w") as devnull:
            os.dup2(devnull.fileno(), stdout_fd)
            yield
    finally:
        # Restore the original terminal output to FD 1
        os.dup2(saved_stdout_fd, stdout_fd)
        os.close(saved_stdout_fd)


class DebuggerAbstraction(ABC):
    @abstractmethod
    def set_breakpoint(self, location: str):
        pass

    @abstractmethod
    def set_breakpoints_at_tags(self, function: str, tags: List[int]):
        pass

    @abstractmethod
    def get_current_line(self) -> str:
        pass

    @abstractmethod
    def get_variable_printer(self, variable_name) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Get both summary and children names and summaries from a variable name

        Raises a RuntimeError if the variable cannot be parsed
        """
        pass

    @staticmethod
    def _find_tags(
        filepath: str, function_name: str, start_line: int, tags: List[int]
    ) -> List[str]:
        tags_lines: List[str] = []
        with open(filepath, "r") as f:
            # Skip lines until we reach the start of the line
            lines = islice(f, start_line - 1, None)
            crt_line = start_line

            for tag in tags:
                pattern = f"/// {function_name}::{tag}"
                try:
                    while lines.__next__().find(pattern) == -1:
                        crt_line += 1
                    # we found it
                    tags_lines.append(f"{filepath}:{crt_line}")
                    crt_line += 1
                except StopIteration:
                    raise RuntimeError(
                        f"Could not find tag {function_name}{tag} in {filepath}"
                    )
        return tags_lines

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def continue_(self):
        pass

    @abstractmethod
    def execute(self, command: str) -> str:
        pass
