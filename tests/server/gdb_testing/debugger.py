from typing import List
import gdb  # type: ignore

from common.debugger import DebuggerAbstraction, stdout_silence


class GdbDebugger(DebuggerAbstraction):
    def set_breakpoint(_, location: str):
        gdb.execute(f"b {location}", to_string=True)

    def get_current_line(self) -> str:
        loc = gdb.decode_line()[1][0]
        return f"{loc.symtab.filename}:{loc.line}"

    def set_breakpoints_at_tags(self, function: str, tags: List[int]):
        unparsed, parsed = gdb.decode_line(function)
        if unparsed:
            raise RuntimeError(f"Could not find function {function}")

        tags.sort()
        loc: gdb.Symtab_and_line = parsed[0]
        filename = loc.symtab.fullname()

        tags_lines = self._find_tags(filename, function, loc.line, tags)
        for tag_line in tags_lines:
            self.set_breakpoint(tag_line)

    def run(_):
        with stdout_silence():
            gdb.execute("run", to_string=True)

    def continue_(_):
        with stdout_silence():
            gdb.execute("continue", to_string=True)

    def execute(_, command) -> str:
        return gdb.execute(command, to_string=True)
