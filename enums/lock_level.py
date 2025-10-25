from enum import IntEnum

class LockLevel(IntEnum):
    UNLOCKED = 0
    LOCKED = 1
    DOUBLE_LOCKED = 2
