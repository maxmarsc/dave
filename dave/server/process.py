from __future__ import annotations
from dataclasses import dataclass
import multiprocessing as mp
from multiprocessing.connection import Connection
import os
import subprocess
from typing import Dict, List, Union
from enum import Enum
from pathlib import Path


from .entity import Entity
from .future_gdb import blocked_signals
from .debuggers.value import DebuggerMemoryError

from dave.common.singleton import SingletonMeta
from dave.common.logger import Logger
from dave.common.raw_entity import RawEntity, RawEntityList

from dave.common.server_type import *

try:
    DAVE_VENV_PATH = Path(os.environ["DAVE_VENV_FOLDER"]) / "bin/activate"
except KeyError:
    DAVE_VENV_PATH = Path.home() / ".dave/venv/bin/activate"


class DaveProcess(metaclass=SingletonMeta):
    """
    A singleton class that handles the management of the client (gui) process of dave

    Since you have no garranties on the python interpreter used by the debugger,
    dave needs to start another completely independent process, using a dedicated
    venv.
    """

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
        self.__entities: Dict[int, Entity] = dict()
        self.__dbgr_con, self.__gui_con = mp.Pipe()
        self.__process = None

    def start(self, use_external_env=True):
        """
        Starts the dave GUI process.

        If the process was terminated calling this method will recreate it from
        scratch

        Parameters
        ----------
        use_external_env : bool, optional
            Use the dedicated dave venv to start the new process, by default True

        Raises
        ------
        RuntimeError
            If the GUI process is already running
        """
        if self.__process is not None:
            if self.is_alive():
                raise RuntimeError("Dave process was already started")
            else:
                # Process already ran and exit, needs to reset the object
                self.__process = None
                self.__entities = dict()
                self.__dbgr_con, self.__gui_con = mp.Pipe()

        if use_external_env:
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
        else:
            self.__process = subprocess.Popen(
                args=["python -m dave.client {}".format(self.__gui_con.fileno())],
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
        """
        Check every entity tracked by dave :
        - if a entity is in scope, this will read the samples from the debugger
        memory and sends and update
        - if a entity is not in scope, this will tell it to the gui

        **Note:** If reading the memory of an entity fails (likely because it is
        unitialized or deallocated), it will be considered out of scope
        """
        # First check for delete messages
        self.__handle_incoming_messages()

        # Then update all the entities that are in the current scope
        for entity in self.__entities.values():
            id = entity.id
            if not entity.in_scope:
                Logger().debug(f"{id}:{entity.name} is out of scope")
                self.__dbgr_con.send(RawEntity.OutScopeUpdate(id))
            else:
                Logger().debug(f"{id}:{entity.name} is in scope")
                try:
                    update = entity.as_raw().as_update()
                    self.__dbgr_con.send(update)
                except DebuggerMemoryError as e:
                    self.__log_out_of_scope(entity, e)
                    self.__dbgr_con.send(RawEntity.OutScopeUpdate(id))

    def add_to_model(self, entities: List[Entity]):
        entity_list = list()
        for entity in entities:
            # Add the entity to the tracking list for future iterations
            assert entity.id not in self.__entities
            self.__entities[entity.id] = entity
            try:
                # Try to read the memory and create a RawEntity to send to the client
                entity_list.append(entity.as_raw())
            except DebuggerMemoryError as e:
                self.__log_out_of_scope(entity, e)
                # Send a RawEntity with no samples instead, we will send the samples
                # once the Entity is in scope and readable
                entity_list.append(entity.as_empty_raw())

        # Send the new entities to the client
        self.__dbgr_con.send(RawEntityList(entity_list))

    @staticmethod
    def __log_out_of_scope(entity: Entity, error: Exception):
        Logger().warning(
            f"Failed to read entity {entity.id}:{entity.name}. Might be deallocated or unitialized. It will be considered out of scope."
        )
        Logger().warning(f"Failed with {error.args[0]}")

    def __identify_entity(self, id: str) -> int:
        try:
            return int(id)
        except ValueError:
            for container in self.__entities.values():
                if container.name == id:
                    return container.id
        return -1

    def freeze(self, id: str) -> bool:
        """
        Freeze/Unfreeze an entity. Returns True on success.

        Parameters
        ----------
        id : str
            Either the name or the int id of an entity. When using the name, if
            several entities have the same name, the first created will be deleted
        """
        # First check for delete messages
        self.__handle_incoming_messages()

        id = self.__identify_entity(id)

        # wtf is this flagged as unreachable
        if id not in self.__entities:
            return False

        self.__dbgr_con.send(DaveProcess.FreezeMessage(id))
        return True

    def concat(self, id: str) -> bool:
        """
        Enable/Disable the concatenation feature of an entity. Returns True on success.
        Can fail if the entity does not support concatenation.

        Parameters
        ----------
        id : str
            Either the name or the int id of a entity. When using the name, if
            several entities have the same name, the first created will be deleted
        """
        # First check for delete messages
        self.__handle_incoming_messages()

        id = self.__identify_entity(id)

        # wtf is this flagged as unreachable
        if id not in self.__entities:
            return False

        if not self.__entities[id].supports_concat():
            return False

        self.__dbgr_con.send(DaveProcess.ConcatMessage(id))
        return True

    def delete(self, id: str) -> bool:
        """
        Mark an entity as to be deleted. Returns True on success.

        This method does not actually delete the entity. It sends a message to
        the gui that the entity should be deleted.

        Parameters
        ----------
        id : str
            Either the name or the int id of a entity. When using the name, if
            several entities have the same name, the first created will be deleted
        """
        # First check for delete messages
        self.__handle_incoming_messages()

        id = self.__identify_entity(id)

        if id not in self.__entities:
            return False

        # wtf is this flagged as unreachable
        self.__dbgr_con.send(DaveProcess.DeleteMessage(id))
        return True

    def __handle_incoming_messages(self):
        while self.__dbgr_con.poll():
            try:
                msg = self.__dbgr_con.recv()
                if isinstance(msg, DaveProcess.DeleteMessage):
                    Logger().debug(
                        f"Debugger process received delete command for {msg.id}"
                    )
                    del self.__entities[msg.id]
            except EOFError:
                Logger().debug("Received EOF from GUI process")
