from __future__ import annotations
from dataclasses import dataclass
from enums.lock_level import LockLevel
from models.coord import Coord
from models.inventory import Inventory
from items.permanent_item import PermanentItem

@dataclass
class Door:
    _lock: LockLevel
    _leads_to: Coord

    @property
    def lock(self) -> LockLevel:
        return self._lock

    @lock.setter
    def lock(self, value: LockLevel) -> None:
        self._lock = value

    @property
    def leads_to(self) -> Coord:
        return self._leads_to

    @leads_to.setter
    def leads_to(self, value: Coord) -> None:
        self._leads_to = value

    def can_open(self, inv: Inventory) -> bool:
        if self._lock == LockLevel.UNLOCKED:
            return True
        if self._lock == LockLevel.LOCKED and PermanentItem.LOCKPICK_KIT in inv.tools:
            return True
        return inv.keys > 0

    def open(self, inv: Inventory) -> bool:
        """Consomme une clé si nécessaire (sauf lockpick sur niveau 1)."""
        if self._lock == LockLevel.UNLOCKED:
            return True
        if self._lock == LockLevel.LOCKED and PermanentItem.LOCKPICK_KIT in inv.tools:
            return True
        if inv.keys <= 0:
            return False
        inv.keys -= 1
        return True
