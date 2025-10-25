from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from enums.direction import Direction
from models.door import Door
from rooms.room_base import Room

@dataclass
class Cell:
    _room: Room | None = None
    _doors: Dict[Direction, Door] = field(default_factory=dict)

    @property
    def room(self) -> Room | None:
        return self._room

    @room.setter
    def room(self, value: Room | None) -> None:
        self._room = value

    @property
    def doors(self) -> Dict[Direction, Door]:
        return self._doors

    @doors.setter
    def doors(self, value: Dict[Direction, Door]) -> None:
        self._doors = value
