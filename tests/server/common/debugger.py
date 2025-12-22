from abc import ABC, abstractmethod
from typing import List, Deque
from itertools import islice
from collections import deque


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
