from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Coord:
    """Coordonnée d'une case du manoir, définie par sa ligne (r) et sa colonne (c)."""
    r: int
    c: int
