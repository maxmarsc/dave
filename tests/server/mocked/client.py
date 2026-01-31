from multiprocessing.connection import Connection
import subprocess
from typing import Any, List
import os
from unittest.mock import MagicMock, patch

from dave.common.singleton import SingletonMeta
from dave.server.process import DaveProcess


def patch_client_popen(test_method):
    """
    Decorator to patch automatically the Popen call in DaveProcess
    """

    def side_effect(*args, **kwargs):
        # Intercept the FD
        pass_fds = kwargs.get("pass_fds", [])
        if pass_fds:
            fd = pass_fds[0]
            # Hand it to our Singleton Client
            MockClient().connect_from_fd(fd)

        # Create a fake Process object
        # We use MagicMock for simplicity, but you can use the __new__ trick if you prefer
        mock_process = MagicMock()
        mock_process.pid = 1234
        mock_process.returncode = None

        # Wire the .wait() call to our custom logic
        mock_process.wait.side_effect = MockClient().wait
        mock_process.poll.side_effect = MockClient().poll

        return mock_process

    return patch("dave.server.process.subprocess.Popen", side_effect=side_effect)(
        test_method
    )


class MockClient(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.__connection: Connection = None
        self.reset()

    def reset(self):
        if self.__connection:
            self.__connection.close()
            self.__connection = None

    def connect_from_fd(self, fd: int):
        """Called by the Popen patch to establish the connection."""
        # Duplicate the FD so we own this copy
        self.__connection = Connection(os.dup(fd))

    def send_from_client(self, msg):
        if self.__connection is None:
            raise RuntimeError("Sending on a non-connected mock client")
        self.__connection.send(msg)

    def receive_from_server(self, timeout=0.01) -> List[Any]:
        """
        Returns all the messages received from the server. This will also
        trigger internal reactions to messages (like DeleteMessage)
        """
        if self.__connection is None:
            raise RuntimeError("Try to receive on a non-connected mock client")
        received = list()
        while self.__connection.poll(timeout):
            new_msg = self.__connection.recv()
            self.__react_to_msg(new_msg)
            received.append(new_msg)
        return received

    def __react_to_msg(self, msg):
        match msg:
            case DaveProcess.DeleteMessage(id=id):
                # Signal we deleted the entity
                self.__connection.send(DaveProcess.DeleteMessage(id=id))
            case _:
                pass

    def wait(self):
        """
        Mocking the wait function of Popen

        This will raise an error if no STOP message was sent before
        """
        if self.__connection is None:
            return 0

        received = self.receive_from_server(0.01)
        if not received or received[-1] != DaveProcess.Message.STOP:
            raise RuntimeError("Called Popen.wait without sending a STOP message")

        self.reset()
        return 0

    def poll(self):
        if self.__connection is None:
            return 0
        return None
