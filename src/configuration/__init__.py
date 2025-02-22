from enum import Enum

from .v1 import Configuration as ConfigurationV1

class ConfigurationSpecification(Enum):
    """
    Configuration types.
    """
    V0 = "v0 is reserved to indicate no version.",
    V1 = {
        "version": "bench-cfg-v1",
        "config": ConfigurationV1,
    }
