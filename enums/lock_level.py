from enum import IntEnum

class LockLevel(IntEnum):
    """Niveaux de verrouillage possibles pour une porte."""
    UNLOCKED = 0
    LOCKED = 1
    DOUBLE_LOCKED = 2
