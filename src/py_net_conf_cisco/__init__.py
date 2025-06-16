# from .interface_datamodel import InterfaceConfig

from .ciscoconf import CiscoConfig
from .interface_datamodel import InterfaceConfig

__version__ = "0.1.0"
__all__ = [
    "InterfaceConfig",
    "CiscoConfig",
]


def hello() -> str:
    return "Hello from py-net-conf-cisco!"
