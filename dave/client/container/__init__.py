from dave.client.entity import ModelFactory
from dave.common.raw_container import RawContainer
from .container_model import ContainerModel

ModelFactory().register(RawContainer, ContainerModel)
