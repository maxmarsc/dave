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

    START_METHOD = "spawn"

    def __init__(self) -> None:
        self.__containers: Dict[int, Container] = dict()
        if SERVER_TYPE == ServerType.LLDB:
            # On LLDB we can use a context
            self.__ctx = mp.get_context(DaveProcess.START_METHOD)
        else:
            # But not in GDB, dark magic probably
            self.__ctx = mp
            self.__ctx.set_start_method(DaveProcess.START_METHOD, force=True)
        # Make sure we start the GUI process from the python executable from the PATH
        self.__ctx.set_executable(
            subprocess.check_output(
                ". {};which python".format(DAVE_VENV_PATH), shell=True
            )
            .strip()
            .decode("utf-8")
        )
        self.__dbgr_con, self.__gui_con = self.__ctx.Pipe()
        self.__process = None

    def start(self):
        if self.__process is not None:
            if self.__process.is_alive():
                raise RuntimeError("Dave process was already started")
            elif self.__process.exitcode is not None:
                # Process already ran and exit, needs to reset the object
                self.__process = None
                self.__containers = dict()
                self.__dbgr_con, self.__gui_con = self.__ctx.Pipe()

        with blocked_signals():
            self.__process = self.__ctx.Process(
                target=DaveProcess.create_and_run,
                args=(self.__gui_con,),
            )
            self.__process.start()

    @staticmethod
    def create_and_run(gui_conn: Connection):
        """
        ! This should never be called from the debugger process !

        Starts the GUI thread
        """
        # First make sure the import path are the one from the new env
        # import sys
        sys.path = (
            subprocess.check_output(
                '. {};python -c "import os,sys;print(os.linesep.join(sys.path).strip())"'.format(
                    DAVE_VENV_PATH
                ),
                shell=True,
            )
            .decode("utf-8")
            .split()
        )
        try:
            from dave.client import DaveGUI
        except ImportError as e:
            Logger().get().critical(
                "Tried to load GUI from incompatible interpreter\n"
                f"sys.executable : {sys.executable}\n"
                f"sys.path : {sys.path}\n"
            )
            raise e

        Logger().get().debug("Starting GUI process")
        gui = DaveGUI(gui_conn)
        gui.run()

    def is_alive(self) -> bool:
        if self.__process is not None:
            return self.__process.is_alive()
        return False

    def should_stop(self):
        self.__dbgr_con.send(DaveProcess.Message.STOP)

    def join(self):
        self.__process.join()

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
