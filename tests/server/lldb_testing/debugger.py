from typing import List, Tuple
from pathlib import Path
import os

import lldb

from common.debugger import CommandError, DebuggerAbstraction


def synthetic_child_generator(value: lldb.SBValue):
    num_synthetic_children = (
        value.GetNumChildren() - value.GetNonSyntheticValue().GetNumChildren()
    )
    for child_idx in range(num_synthetic_children):
        yield value.GetChildAtIndex(child_idx)


class LldbDebugger(DebuggerAbstraction):
    def __init__(self):
        self.__target: lldb.SBTarget = None
        self.__process: lldb.SBProcess = None

    def set(self, target: lldb.SBDebugger):
        self.__target = target

    def unset(self):
        self.__target = None
        self.__process = None

    def set_breakpoint(self, location: str):
        if self.__target is None:
            raise RuntimeError("LldbDebugger is not set")
        if ":" in location:
            filename, line = location.split(":")
            # Use ResolveFileSpec to handle partial paths robustly
            self.__target.BreakpointCreateByLocation(filename, int(line))
        else:
            self.__target.BreakpointCreateByName(location)

    def get_current_line(self) -> str:
        if not self.__process or not self.__process.IsValid():
            raise RuntimeError("Process is not alive")

        thread: lldb.SBThread = self.__process.GetSelectedThread()
        frame: lldb.SBFrame = thread.GetSelectedFrame()
        line_entry: lldb.SBLineEntry = frame.GetLineEntry()

        if not line_entry.IsValid():
            raise RuntimeError("Failed to retrieve current line")
        file_spec: lldb.SBFileSpec = line_entry.GetFileSpec()
        return f"{file_spec.GetFilename()}:{line_entry.GetLine()}"

    def get_variable_printer(
        self, variable_name: str
    ) -> Tuple[str, List[Tuple[str, str]]]:
        try:
            val: lldb.SBValue = (
                lldb.debugger.GetSelectedTarget()
                .GetProcess()
                .GetSelectedThread()
                .GetSelectedFrame()
                .FindVariable(variable_name)
            )
            if not val.IsValid():
                raise Exception()
        except:
            raise RuntimeError(f"Failed to find and eval {variable_name}")

        synthetic_children = [
            (child.name, child.summary) for child in synthetic_child_generator(val)
        ]
        return (val.summary, synthetic_children)

    def set_breakpoints_at_tags(self, function: str, tags: List[str]):
        # Resolve function to find the file and start line
        context_list: lldb.SBSymbolContextList = self.__target.FindFunctions(function)
        if context_list.GetSize() == 0:
            raise RuntimeError(f"Could not find function {function}")

        sbfunction: lldb.SBFunction = context_list.functions[0]
        line_entry: lldb.SBLineEntry = sbfunction.GetStartAddress().line_entry

        # # Use the first match
        # context: lldb.SBSymbolContext = context_list.GetContextAtIndex(0)
        # line_entry: lldb.SBLineEntry = context.GetLineEntry()
        if not line_entry.IsValid():
            raise RuntimeError(f"No line info for function {function}")

        # Get the full path
        file_spec: lldb.SBFileSpec = line_entry.GetFileSpec()
        directory = Path(file_spec.GetDirectory())
        full_path: Path = directory / file_spec.GetFilename()
        start_line = line_entry.GetLine()
        tags.sort()

        tags_lines = self._find_tags(full_path.resolve(), function, start_line, tags)

        for tag_line in tags_lines:
            self.set_breakpoint(tag_line)

    def run(self):
        if self.__target is None:
            raise RuntimeError("LldbDebugger is not set")
        self.__process = self.__target.LaunchSimple(None, None, os.getcwd())

        if not self.__process.IsValid():
            raise RuntimeError("Failed to launch process")

    def continue_(self):
        if not self.__process:
            raise RuntimeError("Process not started")

        error: lldb.SBError = self.__process.Continue()
        if not error.Success():
            raise RuntimeError(f"Failed to continue: {error}")

    def execute(self, command) -> str:
        res = lldb.SBCommandReturnObject()
        self.__target.GetDebugger().GetCommandInterpreter().HandleCommand(command, res)

        if res.Succeeded():
            return res.GetOutput() or ""
        else:
            err_txt = res.GetError().removeprefix("error: ").removesuffix("\n")
            raise CommandError(f"{err_txt}")
