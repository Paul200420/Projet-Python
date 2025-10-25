from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from models.cell import Cell
from models.coord import Coord

@dataclass
class Manor:
    _rows: int = 5
    _cols: int = 9
    _grid: List[List[Cell]] = field(default_factory=lambda: [[Cell() for _ in range(9)] for _ in range(5)])
    _start: Coord = Coord(4, 4)  
    _goal: Coord = Coord(0, 4)   

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
        return 0 <= c.r < self._rows and 0 <= c.c < self._cols

    def cell(self, c: Coord) -> Cell:
        return self._grid[c.r][c.c]
