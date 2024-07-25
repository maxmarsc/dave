from __future__ import annotations
import multiprocessing
import queue
from typing import Dict, List, Union
from enum import Enum

from .gui import GaveGUI
from .container import Container
from .future_gdb import blocked_signals
from .container_model import ContainerModel
from .singleton import SingletonMeta


class GaveProcess(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.__containers: Dict[int, Container] = dict()
        self.__cqueue = multiprocessing.Queue()
        self.__pqueue = multiprocessing.Queue()
        self.__process = None

    def start(self, monitor_live_signal: bool = False):
        if isinstance(self.__process, multiprocessing.Process):
            if self.__process.is_alive():
                raise RuntimeError("Dave process was already started")
            elif self.__process.exitcode is not None:
                # Process already ran and exit, needs to reset the object
                self.__process = None
                self.__containers = dict()

        old_spawn_method = multiprocessing.get_start_method()
        with blocked_signals():
            if old_spawn_method != "spawn":
                multiprocessing.set_start_method("spawn", force=True)
            self.__process = multiprocessing.Process(
                target=GaveGUI.create_and_run,
                args=(self.__cqueue, self.__pqueue, monitor_live_signal),
            )
            if old_spawn_method != "spawn":
                multiprocessing.set_start_method(old_spawn_method, force=True)
            self.__process.start()

    def is_alive(self) -> bool:
        if self.__process is not None:
            return self.__process.is_alive()
        return False

    def should_stop(self):
        self.__cqueue.put(GaveGUI.Message.STOP)

    def join(self):
        self.__process.join()

    def dbgr_update_callback(self):
        # First check for delete messages
        self.__handle_incoming_messages()

        # Then update all the containers
        for container in self.__containers.values():
            data = container.read_from_debugger()
            id = container.id
            self.__cqueue.put(ContainerModel.Update(id, data))
            print(f"update sent {id} {data.shape}")

    def add_to_model(self, container: Container):
        self.__containers[container.id] = container
        self.__cqueue.put(container.as_raw())

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

        try:
            id = int(id)
        except ValueError:
            for container in self.__containers.values():
                if container.name == id:
                    id = container.id
                    break

        if id not in self.__containers:
            return False

        # wtf is this flagged as unreachable
        self.__cqueue.put(GaveGUI.DeleteMessage(id))
        return True

    def live_signal(self):
        self.__cqueue.put(GaveGUI.Message.DBGR_IS_ALIVE)

    def __handle_incoming_messages(self):
        while True:
            try:
                msg = self.__pqueue.get_nowait()
                if isinstance(msg, GaveGUI.DeleteMessage):
                    del self.__containers[msg.id]
            except queue.Empty:
                break
