import logging
import os
from .singleton import SingletonMeta

from . import server_type as st


class Logger(
    metaclass=SingletonMeta,
):
    """
    Custom logger class

    Used to abstract the logs functions depending on the server
    """

    def __init__(self):
        logging.basicConfig(format="%(levelname)s: %(message)s")
        self.__level = os.environ.get("DAVE_LOGLEVEL", "INFO").upper()
        if st.SERVER_TYPE != st.ServerType.GDB:
            self.__init_logger()
        else:
            try:
                import gdb

                self.__logger = None
            except ModuleNotFoundError:
                self.__init_logger()

    def __init_logger(self):
        self.__logger = logging.getLogger("dave")
        self.__logger.setLevel(self.__level)

    def info(self, message: str):
        if self.__logger is None:
            import gdb

            gdb.write(f"INFO: {message}\n")
        else:
            self.__logger.info(message)

    def warning(self, message: str):
        if self.__logger is None:
            import gdb

            gdb.write(f"WARNING: {message}\n")
        else:
            self.__logger.warning(message)

    def debug(self, message: str):
        if self.__level == "DEBUG":
            if self.__logger is None:
                import gdb

                gdb.write(f"DEBUG: {message}\n")
            else:
                self.__logger.debug(message)

    def error(self, message: str):
        if self.__logger is None:
            import gdb

            gdb.write(f"ERROR: {message}\n")
        else:
            self.__logger.error(message)
