from typing import List, Tuple
import gdb  # type: ignore

from common.debugger import DebuggerAbstraction, stdout_silence


class GdbDebugger(DebuggerAbstraction):
    def set_breakpoint(_, location: str):
        gdb.execute(f"b {location}", to_string=True)

    def get_current_line(self) -> str:
        loc = gdb.decode_line()[1][0]
        return f"{loc.symtab.filename}:{loc.line}"

    def get_variable_printer(
        self, variable_name: str
    ) -> Tuple[str, List[Tuple[str, str]]]:
        try:
            val = gdb.parse_and_eval(variable_name)
        except:
            raise RuntimeError(f"Failed to find and eval {variable_name}")
        real_type = val.type.strip_typedefs()
        real_type_fields = {
            f.name for f in real_type.fields() if hasattr(f, "name") and f.name
        }

        visualizer = gdb.default_visualizer(val)
        synthetic_children: List[Tuple[str, str]] = list()
        for name, value in visualizer.children():
            if name not in real_type_fields:
                synthetic_children.append((name, str(value)))
        # children = [(name, str(value)) for (name, value) in visualizer.children()]
        return (visualizer.to_string(), synthetic_children)

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
