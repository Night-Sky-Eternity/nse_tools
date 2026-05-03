from enum import Enum, auto
from typing import Literal

__all__ = ["FREE", "MISSING", "FreeType", "MissingType"]


class Sentinel(Enum):
    MISSING = auto()
    FREE = auto()


MISSING = Sentinel.MISSING
type MissingType = Literal[Sentinel.MISSING]

FREE = Sentinel.FREE
type FreeType = Literal[Sentinel.FREE]
