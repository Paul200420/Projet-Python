from __future__ import annotations
from enum import Enum, auto

class Direction(Enum):
    """Représente les quatre directions utilisées pour les déplacements."""
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    @staticmethod
    def delta(d: "Direction") -> tuple[int, int]:
        """Retourne le déplacement (dr, dc) correspondant à une direction donnée."""
        if d is Direction.UP: return (-1, 0)
        if d is Direction.DOWN: return (1, 0)
        if d is Direction.LEFT: return (0, -1)
        if d is Direction.RIGHT: return (0, 1)
        raise ValueError("Unknown direction")
