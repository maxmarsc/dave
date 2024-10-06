import re
from typing import Tuple
import numpy as np

from dave.server.container import SampleType, Container2D
from dave.server.container_factory import ContainerFactory


class NumpyArray(Container2D):
    """
    Match any 2D numpy container
    """

    __REGEX = r"<class 'numpy.ndarray'>"

    def __init__(self, pdb_value: object, name: str, _):
        assert isinstance(pdb_value, np.ndarray)
        if len(pdb_value.shape) > 2:
            raise TypeError(f"Numpy array support is limited to 1D and 2D arrays")

        data_type = SampleType.from_numpy(pdb_value.dtype)
        super().__init__(pdb_value, name, data_type)

    def shape(self) -> Tuple[int, int]:
        assert isinstance(self._value, np.ndarray)
        if len(self._value.shape) == 1:
            return (1, self._value.shape[0])
        return (self._value.shape[0], self._value.shape[1])

    @classmethod
    def typename_matcher(cls) -> re.Pattern:
        return re.compile(cls.__REGEX)

    def read_from_debugger(self) -> np.ndarray:
        assert isinstance(self._value, np.ndarray)
        return self._value.reshape(self.shape())


ContainerFactory().register(NumpyArray)
