from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List
import random

from objects.base import GameObject
from objects.consumable import Apple, Banana, Cake, Sandwich, Meal
from objects.permanent import ShovelObj, HammerObj, LockpickKitObj, MetalDetectorObj, RabbitFootObj
from items.permanent_item import PermanentItem


@dataclass
class InteractiveObject(GameObject):
    """
    Classe de base pour les objets interactifs (coffres, spots, casiers).
    """
    _required_tools: List[PermanentItem] = field(default_factory=list)   # outils permanents nécessaires (ex: marteau)
    _can_use_key: bool = False                                           # est-ce qu'une clé peut être utilisée
    _loot_table: List[GameObject] = field(default_factory=list)          # objets possibles
    _can_be_empty: bool = False                                          # l'objet peut-il être vide ?

    @property
    def required_tools(self) -> List[PermanentItem]:
        return self._required_tools

    @required_tools.setter
    def required_tools(self, value: List[PermanentItem]) -> None:
        self._required_tools = value

    @property
    def can_use_key(self) -> bool:
        return self._can_use_key

    @can_use_key.setter
    def can_use_key(self, value: bool) -> None:
        self._can_use_key = value

    @property
    def loot_table(self) -> List[GameObject]:
        return self._loot_table

    @loot_table.setter
    def loot_table(self, value: List[GameObject]) -> None:
        self._loot_table = value

    @property
    def can_be_empty(self) -> bool:
        return self._can_be_empty

    @can_be_empty.setter
    def can_be_empty(self, value: bool) -> None:
        self._can_be_empty = value

    def can_interact(self, game: "Game") -> bool:
        """Vérifie si le joueur peut interagir avec cet objet"""
        inv = game.player.inventory
        has_required_tool = any(tool in inv.tools for tool in self._required_tools)
        has_key = inv.keys > 0 if self._can_use_key else False
        return has_required_tool or has_key or len(self._required_tools) == 0

    def generate_loot(self) -> Optional[GameObject]:
        """Détermine ce que le joueur trouve dans l'objet."""
        if self._can_be_empty and random.random() < 0.3:
            return None
        if not self._loot_table:
            return None
        return random.choice(self._loot_table)

    def on_interact(self, game: "Game") -> str:
        if self.consumed:
            return f"{self.name} est déjà vide."

        inv = game.player.inventory

        # Vérifier les conditions d'ouverture
        has_tool = any(tool in inv.tools for tool in self._required_tools)
        has_key = inv.keys > 0 if self._can_use_key else False

        if not has_tool and not has_key:
            tools_needed = [t.name for t in self._required_tools]
            return f"Vous avez besoin de {tools_needed} ou d'une clé pour ouvrir {self.name}."

        # Consommer une clé si utilisée (et si pas de marteau)
        if has_key and not has_tool:
            inv.keys = inv.keys - 1

        loot = self.generate_loot()
        self.consumed = True

        if loot is None:
            return f"{self.name} est vide..."

        # Déposer le loot dans la room
        game.manor.cell(game.player.pos).room.contents.append(loot)
        return f"Vous avez trouvé {loot.name} dans {self.name}!"


# ================================
# Objets interactifs concrets
# ================================

class Chest(InteractiveObject):
    """Coffre : s'ouvre avec une clé ou un marteau et contient des objets."""
    def __init__(self, image_path: str = "assets/rooms/items/chest.png"):
        super().__init__(
            _name="Chest",
            _image_path=image_path,
            _required_tools=[PermanentItem.HAMMER],  # marteau autorisé
            _can_use_key=True,                      # clé autorisée
            _loot_table=[Apple(), Banana(), Cake(), Sandwich(), Meal(), ShovelObj(), HammerObj()],
            _can_be_empty=False
        )


class DigSpot(InteractiveObject):
    """Endroit à creuser : nécessite la pelle, peut être vide ou donner des objets."""
    def __init__(self, image_path: str = "assets/rooms/items/dig_spot.png"):
        super().__init__(
            _name="Dig Spot",
            _image_path=image_path,
            _required_tools=[PermanentItem.SHOVEL],
            _can_use_key=False,
            _loot_table=[Apple(), Banana(), Sandwich()],
            _can_be_empty=True
        )


class Locker(InteractiveObject):
    """Casier : ne s'ouvre qu'avec une clé."""
    def __init__(self, image_path: str = "assets/rooms/items/locker.png"):
        super().__init__(
            _name="Locker",
            _image_path=image_path,
            _required_tools=[],     # pas de marteau ici
            _can_use_key=True,     # uniquement clé
            _loot_table=[Apple(), Meal(), RabbitFootObj()],
            _can_be_empty=True
        )
