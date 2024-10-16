from __future__ import annotations
from dataclasses import dataclass
import multiprocessing as mp
from multiprocessing.connection import Connection
import queue
import os
import subprocess
import sys
from typing import Dict, List, Union
from enum import Enum
from pathlib import Path


from .container import Container
from .future_gdb import blocked_signals

from dave.common.singleton import SingletonMeta
from dave.common.logger import Logger
from dave.common.raw_container import RawContainer
from dave.common.server_type import *

try:
    DAVE_VENV_PATH = Path(os.environ["DAVE_VENV_FOLDER"]) / "bin/activate"
except KeyError:
    DAVE_VENV_PATH = Path.home() / ".dave/venv/bin/activate"


class DaveProcess(metaclass=SingletonMeta):
    class Message(Enum):
        STOP = "stop"

    @dataclass
    class DeleteMessage:
        id: int

    @dataclass
    class FreezeMessage:
        id: int

    @dataclass
    class ConcatMessage:
        id: int

    def __init__(self) -> None:
        self.__containers: Dict[int, Container] = dict()
        self.__dbgr_con, self.__gui_con = mp.Pipe()
        self.__process = None

    def start(self):
        if self.__process is not None:
            exit_code = self.__process.poll()
            if exit_code is None:
                raise RuntimeError("Dave process was already started")
            else:
                # Process already ran and exit, needs to reset the object
                self.__process = None
                self.__containers = dict()
                self.__dbgr_con, self.__gui_con = mp.Pipe()

        with blocked_signals():
            self.__process = subprocess.Popen(
                args=[
                    ". {};python -m dave.client {}".format(
                        DAVE_VENV_PATH, self.__gui_con.fileno()
                    )
                ],
                shell=True,
                pass_fds=[self.__gui_con.fileno()],
            )

    def is_alive(self) -> bool:
        if self.__process is not None:
            return self.__process.poll() is None
        return False

    def should_stop(self):
        self.__dbgr_con.send(DaveProcess.Message.STOP)

    def join(self):
        self.__process.wait()

    def dbgr_update_callback(self):
        # First check for delete messages
        self.__handle_incoming_messages()

        # Then update all the containers that are in the current scope
        for container in self.__containers.values():
            id = container.id
            if not container.in_scope:
                Logger().get().debug(f"{container.name} is out of scope")
                self.__dbgr_con.send(RawContainer.OutScopeUpdate(id))
            else:
                Logger().get().debug(f"{container.name} is in scope")
                data = container.read_from_debugger()
                shape = container.shape()
                self.__dbgr_con.send(RawContainer.InScopeUpdate(id, data, shape))

    def add_to_model(self, container: Container):
        self.__containers[container.id] = container
        self.__dbgr_con.send(container.as_raw())

    def __identify_container(self, id: str) -> int:
        try:
            return int(id)
        except ValueError:
            for container in self.__containers.values():
                if container.name == id:
                    return container.id
        return -1

    def freeze_container(self, id: str) -> bool:
        """
        Freeze/Unfreeze a container. Returns True on success.

        Parameters
        ----------
        id : str
            Either the name or the int id of a container. When using the name, if
            several container have the same name, the first created will be deleted
        """
        # First check for delete messages
        self.__handle_incoming_messages()

        id = self.__identify_container(id)

        # wtf is this flagged as unreachable
        if id not in self.__containers:
            return False

        self.__dbgr_con.send(DaveProcess.FreezeMessage(id))
        return True

    def concat_container(self, id: str) -> bool:
        """
        Enable/Disable the concatenation feature of a container. Returns True on success.

        Parameters
        ----------
        id : str
            Either the name or the int id of a container. When using the name, if
            several container have the same name, the first created will be deleted
        """
        # First check for delete messages
        self.__handle_incoming_messages()

        id = self.__identify_container(id)

        # wtf is this flagged as unreachable
        if id not in self.__containers:
            return False

        self.__dbgr_con.send(DaveProcess.ConcatMessage(id))
        return True

    def delete_container(self, id: str) -> bool:
        """
        Mark a container as to be deleted. Returns True on success.

        This method does not actually delete the container. It sends a message to
        the gui that the container should be deleted.

        Parameters
        ----------
        id : str
            Either the name or the int id of a container. When using the name, if
            several container have the same name, the first created will be deleted
        """
        # First check for delete messages
        self.__handle_incoming_messages()

        id = self.__identify_container(id)

        if id not in self.__containers:
            return False

        # wtf is this flagged as unreachable
        self.__dbgr_con.send(DaveProcess.DeleteMessage(id))
        return True

    def __handle_incoming_messages(self):
        while self.__dbgr_con.poll():
            try:
                msg = self.__dbgr_con.recv()
                if isinstance(msg, DaveProcess.DeleteMessage):
                    Logger().get().debug(
                        "Debugger process received delete command for {msg.id}"
                    )
                    del self.__containers[msg.id]
            except EOFError:
                Logger().get().debug("Received EOF from GUI process")
