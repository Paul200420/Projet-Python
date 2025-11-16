from __future__ import annotations
from dataclasses import dataclass, field
from typing import Set
from items.permanent_item import PermanentItem

@dataclass
class Inventory:
    """Inventaire du joueur contenant ressources, outils permanents et compteurs spéciaux."""
    # Consommables
    _steps: int = 72
    _gold: int = 0
    _gems: int = 2
    _keys: int = 0
    _dice: int = 1
    # Permanents
    _tools: Set[PermanentItem] = field(default_factory=set)
    # Compteur pour Small Business
    _small_business_count: int = 0

    @property
    def steps(self) -> int:
        return self._steps

    @steps.setter
    def steps(self, value: int) -> None:
        self._steps = value

    @property
    def gold(self) -> int:
        return self._gold

    @gold.setter
    def gold(self, value: int) -> None:
        self._gold = value

    @property
    def gems(self) -> int:
        return self._gems

    @gems.setter
    def gems(self, value: int) -> None:
        self._gems = value

    @property
    def keys(self) -> int:
        return self._keys

    @keys.setter
    def keys(self, value: int) -> None:
        self._keys = value

    @property
    def dice(self) -> int:
        return self._dice

    @dice.setter
    def dice(self, value: int) -> None:
        self._dice = value

    @property
    def tools(self) -> Set[PermanentItem]:
        return self._tools

    # --- utilitaires de base ---
    def spend(self, resource: str, amount: int) -> bool:
        """Tente de dépenser une ressource donnée (steps, gold, gems, keys ou dice)."""
        val = getattr(self, resource)
        if val < amount:
            return False
        setattr(self, resource, val - amount)
        return True

    def add_tool(self, tool: PermanentItem) -> None:
        """Ajoute un outil permanent à l’inventaire."""
        self._tools.add(tool)

    def has_tool(self, tool: PermanentItem) -> bool:
        """Vérifie si l’outil permanent spécifié est déjà possédé."""
        return tool in self._tools

    @property
    def small_business_count(self) -> int:
        return self._small_business_count

    def add_small_business(self) -> bool:
        """
        Ajoute un fragment Small Business.
        Transforme automatiquement 10 fragments en 1 clé.
        Retourne True si une conversion a eu lieu.
        """
        self._small_business_count += 2
        if self._small_business_count >= 10:
            self._small_business_count -= 10
            self._keys += 1
            return True
        return False
