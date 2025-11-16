from dataclasses import dataclass
from rooms.room_base import Room   # <— bon chemin

@dataclass
class RoomDeckItem:
    """Entrée représentant une room dans le deck, avec un indicateur d’inclusion(is in deck)."""
    room: Room
    is_in_deck: bool = True
