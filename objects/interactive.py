from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List
import random

from objects.base import GameObject
from objects.consumable import Apple, Banana, Cake, Sandwich, Meal
from objects.permanent import ShovelObj, HammerObj, LockpickKitObj, MetalDetectorObj, RabbitFootObj
from items.permanent_item import PermanentItem


# =====================================================================
#  Classe de base : on garde les attributs mais on surcharge on_interact
# =====================================================================

@dataclass
class InteractiveObject(GameObject):
    """
    Classe de base pour les objets interactifs (coffres, spots, casiers).
    On garde ces attributs pour compat/affichage, mais le loot vient de
    game.open_container_content(...) dans les classes concrètes.
    """
    _required_tools: List[PermanentItem] = field(default_factory=list)   # outils permanents nécessaires (Enum)
    _can_use_key: bool = False                                           # une clé peut-elle ouvrir ?
    _loot_table: List[GameObject] = field(default_factory=list)          # (non utilisé si on passe par game)
    _can_be_empty: bool = False                                          # (non utilisé si on passe par game)

    @property
    def required_tools(self) -> List[PermanentItem]:
        return self._required_tools

    @property
    def can_use_key(self) -> bool:
        return self._can_use_key

    @property
    def loot_table(self) -> List[GameObject]:
        return self._loot_table

    @property
    def can_be_empty(self) -> bool:
        return self._can_be_empty

    def can_interact(self, game: "Game") -> bool:
        """
        Vrai si le joueur a un outil requis (Enum dans inventory.tools) OU une clé si autorisé,
        OU si aucun outil n'est requis.
        """
        inv = game.player.inventory
        has_required_tool = any(tool in getattr(inv, "tools", set()) for tool in self._required_tools)
        has_key = (inv.keys > 0) if self._can_use_key else False
        return has_required_tool or has_key or len(self._required_tools) == 0

    # NOTE: on ne définit pas ici on_interact ; chaque classe concrète le fait pour
    # appeler game.open_container_content(...) avec le type de loot correspondant.


# ================================
# Objets interactifs concrets
# ================================

# -------- Coffre --------
class Chest(InteractiveObject):
    """Coffre : s'ouvre avec une clé ou un marteau ; loot géré par game.open_container_content('Chest')."""
    def __init__(self, image_path: str = "assets/rooms/items/chest.png"):
        super().__init__(
            _name="Chest",
            _image_path=image_path,
            _required_tools=[PermanentItem.HAMMER],  # marteau autorisé (Enum)
            _can_use_key=True,                      # clé autorisée
            _loot_table=[],                         # ignoré (loot via game)
            _can_be_empty=False
        )

    def on_interact(self, game: "Game") -> str:
        if self.consumed:
            return "Le coffre est vide."

        inv = game.player.inventory
        has_hammer = PermanentItem.HAMMER in getattr(inv, "tools", set())
        has_key = inv.keys > 0 if self._can_use_key else False

        if not (has_hammer or has_key):
            return "Il vous faut un marteau ou une clé pour ouvrir le coffre."

        # Si on n'a pas de marteau et qu'on utilise une clé, la consommer
        if not has_hammer and has_key:
            inv.keys -= 1

        # Loot via game (applique directement or/clé/dé/outils/etc.)
        msg = game.open_container_content("Chest")
        self.consumed = True
        return msg


# -------- Emplacement à creuser --------
class DigSpot(InteractiveObject):
    """Endroit à creuser : nécessite la pelle ; loot via game.open_container_content('Digging')."""
    def __init__(self, image_path: str = "assets/rooms/items/dig_spot.png"):
        super().__init__(
            _name="Dig Spot",
            _image_path=image_path,
            _required_tools=[PermanentItem.SHOVEL],  # pelle requise (Enum)
            _can_use_key=False,
            _loot_table=[],                          # ignoré (loot via game)
            _can_be_empty=True
        )

    def on_interact(self, game: "Game") -> str:
        if self.consumed:
            return "Il n'y a plus rien à creuser."

        inv = game.player.inventory
        has_shovel = PermanentItem.SHOVEL in getattr(inv, "tools", set())
        if not has_shovel:
            return "Il faudrait une pelle pour creuser ici."

        msg = game.open_container_content("Digging")
        self.consumed = True
        return msg


# -------- Casier --------
class Locker(InteractiveObject):
    """
    Casier : s'ouvre uniquement avec une clé.
    Par défaut on réutilise la table de loot 'Chest'. Si tu veux une table dédiée,
    ajoute 'Locker' dans LOOT_TABLES côté game.py et remplace l'appel plus bas.
    """
    def __init__(self, image_path: str = "assets/rooms/items/locker.png"):
        super().__init__(
            _name="Locker",
            _image_path=image_path,
            _required_tools=[],     # pas d'outil
            _can_use_key=True,      # uniquement clé
            _loot_table=[],         # ignoré (loot via game)
            _can_be_empty=True
        )

    def on_interact(self, game: "Game") -> str:
        if self.consumed:
            return "Le casier est vide."

        inv = game.player.inventory
        if not self._can_use_key or inv.keys <= 0:
            return "Ce casier est fermé à clé."

        # Consomme 1 clé
        inv.keys -= 1

        # Utilise la table 'Chest' par défaut ; remplace par 'Locker' si tu l'ajoutes dans game.py
        msg = game.open_container_content("Chest")  # ou "Locker" si LOOT_TABLES["Locker"] existe
        self.consumed = True
        return msg
