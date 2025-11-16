from enum import Enum, auto

class PermanentItem(Enum):
    """Types d'objets permanents que le joueur peut posséder dans son inventaire."""
    SHOVEL = auto()
    HAMMER = auto()
    LOCKPICK_KIT = auto()
    METAL_DETECTOR = auto()
    RABBIT_FOOT = auto()
    SMALL_BUSINESS = auto()  # Fragment qui se transforme en clé quand on en a 10
