from __future__ import annotations
from dataclasses import dataclass
import random
from rooms.room_base import Room
from enums.direction import Direction
from enums.room_colors import CouleurPiece

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
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.BLEUE,
            _effet_texte="Aucun effet."
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
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.BLEUE,
            _effet_texte="Aucun effet."
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
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.VIOLETTE,  
            _effet_texte="Gain de 2 pas possible s'il y a de la bonne nourriture."
        )

    def on_enter(self, game: "Game", r: int, c: int) -> None:
        """30% de chance de +2 pas en entrant."""
        if random.random() < 0.3:
            game.player.inventory.steps += 2

@dataclass
class Pantry(Room):
    """Réserve, salle avec nourriture rare et puissante. == salle de repos"""
    def __init__(self):
        super().__init__(
            _name="Pantry",
            _image_path="assets/rooms/Pantry.png",
            _gem_cost=2,
            _rarity=2,
            _possible_doors={Direction.UP, Direction.DOWN},  # Généralement un cul-de-sac
            _couleur=CouleurPiece.VIOLETTE,
            _effet_texte="Vous vous reposez (+3 pas)."
        )

    def on_enter(self, game: "Game", r: int, c: int) -> None:
        game.player.inventory.steps += 3

@dataclass
class LockerRoom(Room):
    """Salle de casiers, contient uniquement des Locker."""
    def __init__(self):
        super().__init__(
            _name="Locker Room",
            _image_path="assets/rooms/Locker.png",
            _gem_cost=1,
            _rarity=1,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.BLEUE,
            _effet_texte="Peut contenir des casiers à ouvrir."
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
            _possible_doors={Direction.UP, Direction.DOWN},  # Accès limité
            _couleur=CouleurPiece.JAUNE,
            _effet_texte="+4 or trouvé en entrant."
        )

        def treasure_condition(r: int, c: int) -> bool:
            """Ne peut pas apparaître au rez-de-chaussée."""
            return r < 4  # Pas au rez-de-chaussée
        self._placement_condition = treasure_condition

    def on_enter(self, game: "Game", r: int, c: int) -> None:
        game.player.inventory.gold += 4

@dataclass
class Garden(Room):
    """Salle extérieure avec emplacements à creuser."""
    def __init__(self):
        super().__init__(
            _name="Garden",
            _image_path="assets/rooms/Garden.png",
            _gem_cost=1,
            _rarity=1,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.VERTE,  
            _effet_texte="Beau jardin : +1 gemme, 30% de chance d'en trouver une deuxième."
        )

        def garden_condition(r: int, c: int) -> bool:
            """Doit être sur les bords du manoir."""
            return c == 0 or c == 8  # Sur les côtés
        self._placement_condition = garden_condition

    def on_enter(self, game: "Game", r: int, c: int) -> None:
        # Gemme garantie
        game.player.inventory.gems += 1
        # Petit bonus aléatoire
        if random.random() < 0.30:
            game.player.inventory.gems += 1

@dataclass
class Armory(Room):
    """Salle des armements, contient des outils permanents."""
    def __init__(self):
        super().__init__(
            _name="Armory",
            _image_path="assets/rooms/Armory.png",
            _gem_cost=2,
            _rarity=2,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.JAUNE,  
            _effet_texte="Peut obtenir des objets permanents."
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
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.BLEUE,
            _effet_texte="Un dé en plus."
        )

    def on_enter(self, game: "Game", r: int, c: int) -> None:
        """Bonus de chance en entrant."""
        game.player.inventory.dice += 1

@dataclass
class Antechamber(Room):
    """Salle finale du manoir, objectif du jeu."""
    def __init__(self):
        super().__init__(
            _name="Antechamber",
            _image_path="assets/rooms/exit.png",
            _gem_cost=0,  # Ne peut pas être placée normalement
            _rarity=0,    # N'apparaît pas aléatoirement
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.BLEUE,
            _effet_texte="Objectif accompli."
        )
