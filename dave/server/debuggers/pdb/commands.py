# import pdb
from typing import Any, Union, List
import numpy as np
from ...process import DaveProcess

from ...entity_factory import EntityFactory


def show(var: Any, name: str = "", cpx_as_2: bool = False):
    """
    Track and display an audio container using DAVE

    Parameters
    ----------
    var : Any
        The audio container to show
    name : str, optional
        The name of the container to display, default to typename
    cpx_as_2 : bool, optional
        Set to true if the last dimension is of two and is used to represent
        complex values
    """
    if cpx_as_2:
        shape = var.shape  # type: List[int]
        if not shape[-1] == 2:
            raise RuntimeError("cpx_as_2 was provided but last dimension is not 2")
        dims = shape[:-1]
    else:
        dims = var.shape  # type: List[int]

    typename = str(type(var))
    if name == "":
        name = typename

    container = EntityFactory().build(var, typename, name, dims)
    if not DaveProcess().is_alive():
        DaveProcess().start(False)
    DaveProcess().add_to_model(container)
    print(f"Added {name} : {container.id}")


def update():
    if DaveProcess().is_alive():
        DaveProcess().dbgr_update_callback()


def freeze(container_id: Union[str, int]):
    if not DaveProcess().is_alive():
        raise RuntimeWarning("Dave is not started")

    if not DaveProcess().freeze(container_id):
        raise RuntimeWarning(f"{container_id} is not a valid name or container id")


def concat(container_id: Union[str, int]):
    if not DaveProcess().is_alive():
        raise RuntimeWarning("Dave is not started")

    if not DaveProcess().concat(container_id):
        raise RuntimeWarning(f"{container_id} is not a valid name or container id")


def delete(container_id: Union[str, int]):
    if not DaveProcess().is_alive():
        raise RuntimeWarning("Dave is not started")

    if not DaveProcess().delete(container_id):
        raise RuntimeWarning(f"{container_id} is not a valid name or container id")
