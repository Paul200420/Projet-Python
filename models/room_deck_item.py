from dataclasses import dataclass
from rooms.room_base import Room   # <— bon chemin

@dataclass
class RoomDeckItem:
    room: Room
    is_in_deck: bool = True
