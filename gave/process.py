import multiprocessing

from .gui import GaveGUI, StopMessage
from .container_1D import *
from .future_gdb import blocked_signals
from .container_model import ContainerModel
from .singleton import SingletonMeta


class GaveProcess(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.__msg_queue = multiprocessing.Queue()
        old_spawn_method = multiprocessing.get_start_method()
        with blocked_signals():
            if old_spawn_method != "spawn":
                multiprocessing.set_start_method("spawn", force=True)
            self.__process = multiprocessing.Process(
                target=GaveGUI.create_and_run, args=(self.__msg_queue,)
            )
            if old_spawn_method != "spawn":
                multiprocessing.set_start_method(old_spawn_method, force=True)
        self.__containers: List[Container] = []

    def __del__(self):
        print("Calling GaveProcess destructor")

    def start(self):
        with blocked_signals():
            self.__process.start()

    def is_alive(self) -> bool:
        return self.__process.is_alive()

    def should_stop(self):
        self.__msg_queue.put(StopMessage())

    def join(self):
        self.__process.join()

    def gdb_update_callback(self):
        for container in self.__containers:
            data = container.read_from_gdb()
            id = container.id
            self.__msg_queue.put(ContainerModel.Update(id, data))
            print(f"update sent {id} {data.shape}")

    def add_to_model(self, container: Container):
        self.__containers.append(container)
        # model = ContainerModel(container, 44100)
        # print(f"model sent {model.id, model.variable_name}")
        self.__msg_queue.put(container.as_raw())
