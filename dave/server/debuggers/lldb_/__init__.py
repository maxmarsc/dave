from .commands import (
    StopHook,
    ShowCommand,
    LLDBEventHandler,
    DeleteCommand,
    FreezeCommand,
    ConcatCommand,
    InspectCommand,
    HelpCommand,
)
from .formatters import summary_provider, SyntheticChildrenProvider
import dave.common.server_type as st

st.SERVER_TYPE = st.ServerType.LLDB

from ...languages import *

# If the flag is set, wait for the python debugger to connect
if os.environ.get("DAVE_DEBUG_SERVER") == "1":
    try:
        import debugpy

        print("Waiting for debugger to attach on port 5678...")
        debugpy.listen(("localhost", 5678))
        debugpy.wait_for_client()
        print("Debugger attached! Continuing...")
    except ImportError:
        print("Error: 'debugpy' not found. Cannot attach debugger.")
