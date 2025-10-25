from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Protocol

class Interactable(Protocol):
    def on_interact(self, game: "Game") -> str: ...
    @property
    def consumed(self) -> bool: ...

@dataclass
class GameObject:
    """Base générique pour tout objet posé dans une room (consommable, permanent, etc.)."""
    _name: str
    _image_path: Optional[str] = None
    _consumed: bool = False

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def image_path(self) -> Optional[str]:
        return self._image_path

    @image_path.setter
    def image_path(self, value: Optional[str]) -> None:
        self._image_path = value

    @property
    def consumed(self) -> bool:
        return self._consumed

    @consumed.setter
    def consumed(self, value: bool) -> None:
        self._consumed = value

    def on_interact(self, game: "Game") -> str:
        """Action quand le joueur interagit (ramasse / utilise). Retourne un court message UI."""
        raise NotImplementedError
