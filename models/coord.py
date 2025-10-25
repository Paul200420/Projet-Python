from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Coord:
    r: int
    c: int
