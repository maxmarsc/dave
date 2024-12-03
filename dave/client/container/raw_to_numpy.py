from dave.common.raw_container import RawContainer
import numpy as np

from dave.client.entity.raw_to_numpy import complexify_array, realify_array, to_dtype


def convert_container_data_to_layout(
    data: np.ndarray, layout: RawContainer.Layout
) -> np.ndarray:
    """
    Perform real <-> complex conversion if needed to fit the given data layout
    """
    if layout.is_real:
        return realify_array(data)
    else:
        return complexify_array(data)


def raw_container_to_numpy(raw_container: RawContainer) -> np.ndarray:
    array = np.frombuffer(raw_container.data, dtype=to_dtype(raw_container.sample_type))
    return array.reshape(raw_container.original_shape)
