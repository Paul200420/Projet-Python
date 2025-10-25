from __future__ import annotations
from dataclasses import dataclass
import random
from rooms.room_base import Room
from enums.direction import Direction


# ================================
#  ROOMS OFFICIELLES BLUE PRINCE
# ================================

@dataclass
class EntranceHall(Room):
    """Hall d'entrée, point de départ du joueur."""
    def __init__(self):
        super().__init__(
            _name="Entrance Hall",
            _image_path="assets/rooms/entrance.png",
            _gem_cost=0,  # Gratuit car c'est le départ
            _rarity=0,    # N'apparaît pas aléatoirement
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT}
        )

@dataclass
class PlainRoom(Room):
    """Salle générique sans effet particulier."""
    def __init__(self):
        super().__init__(
            _name="Plain Room",
            _image_path="assets/rooms/sauna.png",
            _gem_cost=0,  # Salle de base, gratuite
            _rarity=0,    # Très commun
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT}
        )

@dataclass
class Kitchen(Room):
    """Salle de cuisine, riche en nourriture."""
    def __init__(self):
        super().__init__(
            _name="Kitchen",
            _image_path="assets/rooms/Kitchen.png",
            _gem_cost=1,
            _rarity=1,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT}
        )
        def kitchen_effect(game: "Game", r: int, c: int) -> None:
            """Chance de trouver de la nourriture en entrant."""
            if random.random() < 0.3:  # 30% de chance
                game.player.inventory.steps += 2
        self._special_effect = kitchen_effect

@dataclass
class Pantry(Room):
    """Réserve, salle avec nourriture rare et puissante."""
    def __init__(self):
        super().__init__(
            _name="Pantry",
            _image_path="assets/rooms/Pantry.png",
            _gem_cost=2,
            _rarity=2,
            _possible_doors={Direction.UP, Direction.DOWN}  # Généralement un cul-de-sac
        )

@dataclass
class LockerRoom(Room):
    """Salle de casiers, contient uniquement des Locker."""
    def __init__(self):
        super().__init__(
            _name="Locker Room",
            _image_path="assets/rooms/Locker.png",
            _gem_cost=1,
            _rarity=1,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT}
        )

@dataclass
class TreasureRoom(Room):
    """Salle de trésor, contient coffres, objets rares et permanents."""
    def __init__(self):
        super().__init__(
            _name="Treasure Room",
            _image_path="assets/rooms/sauna.png",
            _gem_cost=3,  # Coûteux
            _rarity=3,    # Très rare
            _possible_doors={Direction.UP, Direction.DOWN}  # Accès limité
        )
        def treasure_condition(r: int, c: int) -> bool:
            """Ne peut pas apparaître au rez-de-chaussée."""
            return r < 4  # Pas au rez-de-chaussée
        self._placement_condition = treasure_condition

@dataclass
class Garden(Room):
    """Salle extérieure avec emplacements à creuser."""
    def __init__(self):
        super().__init__(
            _name="Garden",
            _image_path="assets/rooms/Garden.png",
            _gem_cost=1,
            _rarity=1,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT}
        )
        def garden_condition(r: int, c: int) -> bool:
            """Doit être sur les bords du manoir."""
            return c == 0 or c == 8  # Sur les côtés
        self._placement_condition = garden_condition

@dataclass
class Armory(Room):
    """Salle des armements, contient des outils permanents."""
    def __init__(self):
        super().__init__(
            _name="Armory",
            _image_path="assets/rooms/Armory.png",
            _gem_cost=2,
            _rarity=2,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT}
        )

@dataclass
class Library(Room):
    """Salle de connaissance, objets spéciaux et de chance."""
    def __init__(self):
        super().__init__(
            _name="Library",
            _image_path="assets/rooms/Library.png",
            _gem_cost=2,
            _rarity=2,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT}
        )
        def library_effect(game: "Game", r: int, c: int) -> None:
            """Bonus de chance en entrant."""
            game.player.inventory.dice += 1
        self._special_effect = library_effect

@dataclass
class Antechamber(Room):
    """Salle finale du manoir, objectif du jeu."""
    def __init__(self):
        super().__init__(
            _name="Antechamber",
            _image_path="assets/rooms/exit.png",
            _gem_cost=0,  # Ne peut pas être placée normalement
            _rarity=0,    # N'apparaît pas aléatoirement
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT}
        )
