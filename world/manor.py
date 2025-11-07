from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from models.cell import Cell
from models.coord import Coord

@dataclass
class Manor:
    """Manoir : 9 lignes (vertical)x 5 colonnes (horizontal)."""

    _rows: int = 9  # hauteur (vertical)
    _cols: int = 5  # largeur (horizontal)
    _grid: List[List[Cell]] = field(default_factory=lambda: [[Cell() for _ in range(5)] for _ in range(9)])
    _start: Coord = Coord(8, 2)   # entrée en bas (ligne 8, colonne 2)
    _goal:  Coord = Coord(0, 2)   # sortie en haut (ligne 0, colonne 2)

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def grid(self) -> List[List[Cell]]:
        return self._grid

    @property
    def start(self) -> Coord:
        return self._start

    @property
    def goal(self) -> Coord:
        return self._goal

    def in_bounds(self, c: Coord) -> bool:
        """Vérifie si la coordonnée est dans la grille."""
        return 0 <= c.r < self._rows and 0 <= c.c < self._cols

    def cell(self, c: Coord) -> Cell:
        """Retourne la cellule en (r, c)."""
        return self._grid[c.r][c.c]
