from __future__ import annotations
import multiprocessing
from typing import List
from enum import Enum

from .gui import GaveGUI
from .container import Container
from .future_gdb import blocked_signals
from .container_model import ContainerModel
from .singleton import SingletonMeta


class GaveProcess(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.__containers: List[Container] = []
        self.__msg_queue = multiprocessing.Queue()
        self.__process = None

    def start(self, monitor_live_signal: bool = False):
        if isinstance(self.__process, multiprocessing.Process):
            if self.__process.is_alive():
                raise RuntimeError("Dave process was already started")
            elif self.__process.exitcode is not None:
                # Process already ran and exit, needs to reset the object
                self.__process = None
                self.__containers = list()

        old_spawn_method = multiprocessing.get_start_method()
        with blocked_signals():
            if old_spawn_method != "spawn":
                multiprocessing.set_start_method("spawn", force=True)
            self.__process = multiprocessing.Process(
                target=GaveGUI.create_and_run,
                args=(self.__msg_queue, monitor_live_signal),
            )
            if old_spawn_method != "spawn":
                multiprocessing.set_start_method(old_spawn_method, force=True)
            self.__process.start()

    def is_alive(self) -> bool:
        if self.__process is not None:
            return self.__process.is_alive()
        return False

    def should_stop(self):
        self.__msg_queue.put(GaveGUI.Message.STOP)

    def join(self):
        self.__process.join()

    def dbgr_update_callback(self):
        for container in self.__containers:
            data = container.read_from_debugger()
            id = container.id
            self.__msg_queue.put(ContainerModel.Update(id, data))
            print(f"update sent {id} {data.shape}")

    def add_to_model(self, container: Container):
        self.__containers.append(container)
        self.__msg_queue.put(container.as_raw())

    def live_signal(self):
        self.__msg_queue.put(GaveGUI.Message.DBGR_IS_ALIVE)
