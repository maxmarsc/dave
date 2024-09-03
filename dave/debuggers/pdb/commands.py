# import pdb
from typing import Any
import inspect
import re
from ...process import DaveProcess

from ...container_factory import ContainerFactory


def show(var: Any, name: str = "", **kwargs):
    # Get the code line that called this function
    # print(var)
    # print(inspect.getframeinfo(inspect.stack()[0].frame.f_back))
    # code_line = (
    #     inspect.getframeinfo(inspect.currentframe().f_back).code_context[0].strip()
    # )
    # Extract the argument name using regex
    # Assuming the function call is somewhat standardized or at least the first argument is 'value'
    # print(code_line)
    # matches = re.search(r"\bpydave\(([^,]+)", code_line)
    # if matches:
    #     var_name = matches.group(1).strip()
    #     print("Argument name passed for 'value':", var_name)
    # else:
    #     print("No argument name found")
    typename = str(type(var))

    container = ContainerFactory().build(var, typename, name)
    if not DaveProcess().is_alive():
        DaveProcess().start()
    DaveProcess().add_to_model(container)


def update():
    if DaveProcess().is_alive():
        DaveProcess().dbgr_update_callback()


# class CustomPyDebugger(pdb.Pdb):
#     def user_line(self, frame):
#         # This method is called when we stop or break at this line
#         print("Breakpoint hit at %s:%d" % (frame.f_code.co_filename, frame.f_lineno))
#         if DaveProcess().is_alive():
#             DaveProcess().gdb_update_callback()

#         super().user_line(frame)


# def set_trace():
#     debugger = CustomPyDebugger()
#     debugger.set_trace()
