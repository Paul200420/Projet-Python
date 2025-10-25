from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Callable, Optional, Set
from enums.direction import Direction

@dataclass
class Room:
    _name: str
    _contents: List["GameObject"] = field(default_factory=list)
    _image_path: str = ""
    _gem_cost: int = 0
    _rarity: int = 0  # 0-3, où 3 est le plus rare
    _possible_doors: Set[Direction] = field(default_factory=set)
    _placement_condition: Optional[Callable[[int, int], bool]] = None
    _special_effect: Optional[Callable[["Game", int, int], None]] = None

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def contents(self) -> List["GameObject"]:
        return self._contents

    @contents.setter
    def contents(self, value: List["GameObject"]) -> None:
        self._contents = value

    @property
    def image_path(self) -> str:
        return self._image_path

    @image_path.setter
    def image_path(self, value: str) -> None:
        self._image_path = value

    @property
    def gem_cost(self) -> int:
        return self._gem_cost

    @gem_cost.setter
    def gem_cost(self, value: int) -> None:
        self._gem_cost = value

    @property
    def rarity(self) -> int:
        return self._rarity

    @rarity.setter
    def rarity(self, value: int) -> None:
        if 0 <= value <= 3:
            self._rarity = value
        else:
            raise ValueError("Rarity must be between 0 and 3")

    @property
    def possible_doors(self) -> Set[Direction]:
        return self._possible_doors

    @possible_doors.setter
    def possible_doors(self, value: Set[Direction]) -> None:
        self._possible_doors = value

    @property
    def placement_condition(self) -> Optional[Callable[[int, int], bool]]:
        return self._placement_condition

    @placement_condition.setter
    def placement_condition(self, value: Optional[Callable[[int, int], bool]]) -> None:
        self._placement_condition = value

    @property
    def special_effect(self) -> Optional[Callable[["Game", int, int], None]]:
        return self._special_effect

    @special_effect.setter
    def special_effect(self, value: Optional[Callable[["Game", int, int], None]]) -> None:
        self._special_effect = value

    def can_be_placed(self, r: int, c: int) -> bool:
        """Vérifie si la pièce peut être placée aux coordonnées données."""
        if self._placement_condition is None:
            return True
        return self._placement_condition(r, c)

    def on_enter(self, game: "Game", r: int, c: int) -> None:
        """Hook d'entrée, exécute l'effet spécial si présent."""
        if self._special_effect is not None:
            self._special_effect(game, r, c)
