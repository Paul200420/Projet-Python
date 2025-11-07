from __future__ import annotations
from dataclasses import dataclass, field
from typing import Set
from items.permanent_item import PermanentItem

@dataclass
class Inventory:
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
        """Tente de dépenser `amount` de (steps|gold|gems|keys|dice)."""
        val = getattr(self, resource)
        if val < amount:
            return False
        setattr(self, resource, val - amount)
        return True

    def add_tool(self, tool: PermanentItem) -> None:
        self._tools.add(tool)

    def has_tool(self, tool: PermanentItem) -> bool:
        return tool in self._tools

    @property
    def small_business_count(self) -> int:
        return self._small_business_count

    def add_small_business(self) -> bool:
        """Ajoute un Small Business et vérifie s'il faut le convertir en clé."""
        self._small_business_count += 2
        if self._small_business_count >= 10:
            self._small_business_count -= 10
            self._keys += 1
            return True  # Indique qu'une conversion a eu lieu
        return False
    

