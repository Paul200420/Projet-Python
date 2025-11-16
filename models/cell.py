from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from enums.direction import Direction
from models.door import Door
from rooms.room_base import Room

@dataclass
class Cell:
    """Représente une case du manoir contenant éventuellement une salle et des portes reliées aux cases voisines."""
    _room: Room | None = None
    _doors: Dict[Direction, Door] = field(default_factory=dict)

    @property
    def room(self) -> Room | None:
        """Retourne la salle associée à cette case, ou None si elle est vide."""
        return self._room

    @room.setter
    def room(self, value: Room | None) -> None:
        """Assigne une salle à cette case du manoir."""
        self._room = value

    @property
    def doors(self) -> Dict[Direction, Door]:
        """Retourne les portes connectées à cette case, indexées par direction."""
        return self._doors

    @doors.setter
    def doors(self, value: Dict[Direction, Door]) -> None:
        """Définit le dictionnaire des portes connectées à cette case."""
        self._doors = value
