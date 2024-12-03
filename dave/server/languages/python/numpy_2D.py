import re
from typing import List, Tuple
import numpy as np

from dave.server.container import SampleType, Container2D
from dave.common.raw_container import RawContainer
from dave.client.container.raw_to_numpy import convert_container_data_to_layout
from dave.client.entity.raw_to_numpy import to_sampletype


class NumpyArray(Container2D):
    """
    Match any 2D numpy container. If the dtype is floating point and the last
    """

    __REGEX = r"<class 'numpy.ndarray'>"

    def __init__(self, pdb_value: object, name: str, dims: List[int]):
        assert isinstance(pdb_value, np.ndarray)
        shape = pdb_value.shape
        # if all(shape[:-1] == dims) and len(dims) >= 1 and len(dims) <= 2:
        if (
            len(dims) >= 1
            and len(dims) <= 2
            and len(shape) == len(dims) + 1
            and shape[:-1] == dims
        ):
            try:
                pdb_value = np.squeeze(
                    convert_container_data_to_layout(
                        pdb_value, RawContainer.Layout.CPX_2D
                    ),
                    axis=-1,
                )
            except RuntimeError:
                dtype = pdb_value.dtype
                raise TypeError(f"Failed to convert {shape} {dtype} to complex layaout")
        elif len(shape) < 0 or len(shape) > 2:
            raise TypeError(f"Numpy array support is limited to 1D and 2D arrays")

        sample_type = to_sampletype(pdb_value.dtype)
        super().__init__(pdb_value, name, sample_type)

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

    @staticmethod
    def formatter_compatible():
        return False


NumpyArray.register()
