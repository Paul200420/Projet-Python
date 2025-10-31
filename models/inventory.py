from __future__ import annotations
from dataclasses import dataclass, field
from typing import Set, Type
from items.permanent_item import PermanentItem

@dataclass
class Inventory:
    # Consommables
    _steps: int = 72
    _gold: int = 0
    _gems: int = 2
    _keys: int = 1
    _dice: int = 0
    # Permanents
    _tools: Set[PermanentItem] = field(default_factory=set)

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
        """Ajoute un outil permanent à l'inventaire."""
        self._tools.add(tool)

    def has_tool(self, tool: PermanentItem) -> bool:
        """Vrai si l'outil exact (instance) est présent."""
        return tool in self._tools

    # --- ✅ NOUVEAU : utile pour tester par CLASSE d'outil (RabbitFootObj, MetalDetectorObj, etc.) ---
    def has_tool_type(self, cls: Type[PermanentItem]) -> bool:
        """Vrai si l'inventaire contient au moins un outil qui est instance de `cls`."""
        return any(isinstance(t, cls) for t in self._tools)

