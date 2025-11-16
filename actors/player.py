from __future__ import annotations
from dataclasses import dataclass, field
from models.coord import Coord
from models.inventory import Inventory

@dataclass
class Player:
    """
    Représente le joueur dans le manoir.

    Attributs :
        _pos (Coord) : Position actuelle du joueur.
        _inventory (Inventory) : Inventaire du joueur.
    """
    _pos: Coord
    _inventory: Inventory = field(default_factory=Inventory)

    @property
    def pos(self) -> Coord:
        """Retourne la position actuelle du joueur."""
        return self._pos

    @pos.setter
    def pos(self, value: Coord) -> None:
        """Modifie la position du joueur."""
        self._pos = value

    @property
    def inventory(self) -> Inventory:
        """Retourne l’inventaire du joueur."""
        return self._inventory

    @inventory.setter
    def inventory(self, value: Inventory) -> None:
        """Modifie l’inventaire du joueur."""
        self._inventory = value
