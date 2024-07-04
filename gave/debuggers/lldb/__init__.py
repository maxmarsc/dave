from .commands import StopHook, ShowCommand

# print("HAHAHAHA")


# def __lldb_init_module(debugger, internal_dict):
#     print("hihou")
#     # Register dave commands
#     debugger.HandleCommand(
#         'command container add -h "A container for my dave commands" gave'
#     )
#     debugger.HandleCommand(f"command script add -f {__name__}.show_command gave show")

#     # Register stop event hook
#     debugger.HandleCommand(f"target stop-hook add -P {__name__}.StopHook")
