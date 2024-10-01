import logging
import os
from .singleton import SingletonMeta


class Logger(
    metaclass=SingletonMeta,
):
    def __init__(self):
        logging.basicConfig(format="%(levelname)s: %(message)s")
        self.__logger = logging.getLogger("dave")
        loglevel = os.environ.get("DAVE_LOGLEVEL", "INFO").upper()
        self.__logger.setLevel(loglevel)
        # self.__logger.config(level=loglevel, format="%(levelname)s: %(message)s")

    def get(self) -> logging.Logger:
        return self.__logger
