from enum import Enum
from typing import Union

SERVER_TYPE = None #type: Union[ServerType, None]

class ServerType(Enum):
    GDB = "gdb"
    LLDB = "lldb"
    PDB = "pdb"