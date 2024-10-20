from dave.common.server_type import SERVER_TYPE, ServerType

SERVER_TYPE = ServerType.PYTHON

from ...languages.python import *
from .commands import show, update, freeze, concat, delete
