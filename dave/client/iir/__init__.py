from dave.client.entity import ModelFactory
from dave.common.raw_iir import RawIir
from .iir_model import IirModel

ModelFactory().register(RawIir, IirModel)
