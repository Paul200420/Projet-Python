from __future__ import annotations
from dataclasses import dataclass, field
from models.coord import Coord
from models.inventory import Inventory

@dataclass
class Player:
    _pos: Coord
    _inventory: Inventory = field(default_factory=Inventory)

    @property
    def pos(self) -> Coord:
        return self._pos

    @pos.setter
    def pos(self, value: Coord) -> None:
        self._pos = value

    @property
    def inventory(self) -> Inventory:
        return self._inventory

    @inventory.setter
    def inventory(self, value: Inventory) -> None:
        self._inventory = value
