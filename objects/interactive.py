from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from objects.base import GameObject
from items.permanent_item import PermanentItem  # Enum stocké dans inventory.tools


# =====================================================================
#  Classe de base : attributs utiles (affichage / règles), le loot est
#  géré par game.open_container_content(...) dans les classes concrètes.
# =====================================================================

@dataclass
class InteractiveObject(GameObject):
    """
    Base pour les objets interactifs (coffres, spots, casiers).
    Le moteur (Game.pick_up_here) retire l'objet si `consumed == True`.
    """
    _required_tools: List[PermanentItem] = field(default_factory=list)  # outils Enum nécessaires
    _can_use_key: bool = False                                         # une clé peut-elle ouvrir ?
    # _loot_table / _can_be_empty non utilisés ici car le loot vient du Game

    @property
    def required_tools(self) -> List[PermanentItem]:
        return self._required_tools

    @property
    def can_use_key(self) -> bool:
        return self._can_use_key

    def can_interact(self, game: "Game") -> bool:
        """
        Vrai si le joueur a un outil requis (Enum) OU une clé si autorisé,
        OU si aucun outil n'est requis.
        """
        inv = game.player.inventory
        has_required_tool = any(tool in getattr(inv, "tools", set()) for tool in self._required_tools)
        has_key = (inv.keys > 0) if self._can_use_key else False
        return has_required_tool or has_key or len(self._required_tools) == 0


# ================================
# Objets interactifs concrets
# ================================

# -------- Coffre --------
class Chest(InteractiveObject):
    """Coffre : s'ouvre avec une clé ou un marteau ; loot via game.open_container_content('Chest')."""
    def __init__(self, image_path: str = "assets/rooms/items/chest.png"):
        super().__init__(
            _name="Chest",
            _image_path=image_path,
            _required_tools=[PermanentItem.HAMMER],  # marteau (Enum)
            _can_use_key=True,
        )

    def on_interact(self, game: "Game") -> str:
        if self.consumed:
            return "Le coffre est vide."

        inv = game.player.inventory
        has_hammer = PermanentItem.HAMMER in getattr(inv, "tools", set())
        has_key = inv.keys > 0 if self._can_use_key else False

        if not (has_hammer or has_key):
            return "Il faut un marteau ou une clé pour ouvrir le coffre."

        # Si on n'a pas de marteau, on consomme 1 clé
        if not has_hammer and has_key:
            inv.keys -= 1

        msg = game.open_container_content("Chest")  # applique directement or/clé/dé/outils/etc.
        self.consumed = True
        return msg


# -------- Emplacement à creuser --------
class DigSpot(InteractiveObject):
    """Endroit à creuser : nécessite la pelle ; loot via game.open_container_content('Digging')."""
    def __init__(self, image_path: str = "assets/rooms/items/dig_spot.png"):
        super().__init__(
            _name="Dig Spot",
            _image_path=image_path,
            _required_tools=[PermanentItem.SHOVEL],  # pelle (Enum)
            _can_use_key=False,
        )

    def on_interact(self, game: "Game") -> str:
        if self.consumed:
            return "Il n'y a plus rien à creuser."

        inv = game.player.inventory
        if PermanentItem.SHOVEL not in getattr(inv, "tools", set()):
            return "Il faut une pelle pour creuser ici."

        msg = game.open_container_content("Digging")
        self.consumed = True
        return msg


# -------- Casier --------
class Locker(InteractiveObject):
    """
    Casier : s'ouvre uniquement avec une clé.
    Par défaut on réutilise la table 'Chest'. Si tu ajoutes LOOT_TABLES['Locker']
    dans game.py, remplace l'appel par 'Locker'.
    """
    def __init__(self, image_path: str = "assets/rooms/items/locker.png"):
        super().__init__(
            _name="Locker",
            _image_path=image_path,
            _required_tools=[],   # aucun outil
            _can_use_key=True,    # clé obligatoire
        )

    def on_interact(self, game: "Game") -> str:
        if self.consumed:
            return "Le casier est vide."

        inv = game.player.inventory
        if inv.keys <= 0:
            return "Ce casier est verrouillé : il faut une clé."

        inv.keys -= 1  # consomme la clé
        msg = game.open_container_content("Chest")  # ou "Locker" si table dédiée
        self.consumed = True
        return msg
