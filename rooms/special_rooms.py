from __future__ import annotations
from dataclasses import dataclass
import random

from rooms.room_base import Room
from enums.direction import Direction
from enums.room_colors import CouleurPiece
from models.coord import Coord
from typing import Type  # si pas déjà importé en haut
# objets interactifs / shop
from objects.interactive import Chest, Vendor

# vrais objets permanents (pas ceux de items.permanent_item)
from objects.permanent import (
    ShovelObj, HammerObj, LockpickKitObj, MetalDetectorObj, RabbitFootObj
)


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
            _gem_cost=0,
            _rarity=0,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.BLEUE,
            _effet_texte="Aucun effet."
        )

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        pass


@dataclass
class PlainRoom(Room):
    """Salle générique sans effet particulier, on peut gagner des smalls business"""
    def __init__(self):
        super().__init__(
            _name="Plain Room",
            _image_path="assets/rooms/sauna.png",
            _gem_cost=0,
            _rarity=1,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.BLEUE,
            _effet_texte="Donnes 2 smalls business une seule fois."
        )
        self._used = False

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        # Give 2 Small Business fragments on each entry
        if self._used :
            return
        try:
            game.player.inventory.add_small_business()
        except Exception:
             # defensive: if inventory lacks the method (older versions), silently ignore
            pass
        self._used = True

    


# -------------------------------------------------
# KITCHEN = shop + petit bonus de pas une seule fois
# -------------------------------------------------
@dataclass
class Kitchen(Room):
    """Salle de cuisine, sert aussi de petite boutique."""
    def __init__(self):
        super().__init__(
            _name="Kitchen",
            _image_path="assets/rooms/Kitchen.png",
            _gem_cost=0,
            _rarity=1,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.JAUNE,
            _effet_texte="30% : +2 pas (1 seule fois). Contient un comptoir, 1–5 pour acheter."
        )
        self._bonus_given = False

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        # 30% de chance de donner +2 pas, mais uniquement la première fois
        if not self._bonus_given:
            if random.random() < 0.30:
                game.player.inventory.steps += 2
            self._bonus_given = True

        # ajoute le shop UNE seule fois dans la pièce
        cell = game.manor.cell(Coord(r, c))
        if not any(isinstance(o, Vendor) for o in cell.room.contents):
            cell.room.contents.append(Vendor())


@dataclass
class Pantry(Room):
    """Réserve / salle de repos."""
    def __init__(self):
        super().__init__(
            _name="Pantry",
            _image_path="assets/rooms/Pantry.png",
            _gem_cost=2,
            _rarity=2,
            _possible_doors={Direction.UP, Direction.DOWN},
            _couleur=CouleurPiece.BLEUE,
            _effet_texte="Vous vous reposez (+3 pas) et obtenez 1 clé (une seule fois)."
        )
        self._used = False

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        if self._used:
            return
        game.player.inventory.steps += 3
        game.player.inventory.keys += 1
        self._used = True


@dataclass
class LockerRoom(Room):
    """Salle de casiers avec un effet de repos : entrer ne coûte aucun pas."""
    def __init__(self):
        super().__init__(
            _name="Locker Room",
            _image_path="assets/rooms/Locker.png",
            _gem_cost=1,
            _rarity=1,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.VIOLETTE,  # Garde sa couleur d'origine
            _effet_texte="Salle de repos : le déplacement vers cette salle ne coûte pas de pas. Peut contenir des casiers à ouvrir."
        )
        

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        # Rembourse le coût du mouvement (1 pas)
        game.player.inventory.steps += 1


@dataclass
class UtilityRoom(Room):
    """Salle d'armoire, stock (+8 or, 15 clés), rare ."""
    def __init__(self):
        super().__init__(
            _name="Treasure Room",
            _image_path="assets/rooms/UtilityCloset.png",
            _gem_cost=3,
            _rarity=3,
            _possible_doors={Direction.UP, Direction.DOWN},
            _couleur=CouleurPiece.JAUNE,
            _effet_texte="+4 or et 1 clé, mais une seule fois. Pas sur la rangée de départ."
        )
        self._taken = False

        def treasure_condition(r: int, c: int) -> bool:
            return r < 4  # pas sur la rangée de départ
        self._placement_condition = treasure_condition

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        if self._taken:
            return
        game.player.inventory.gold += 8
        game.player.inventory.keys += 15
        self._taken = True


@dataclass
class Garden(Room):
    """Jardin : +1 gemme (et 30% de chance +1) — effet donné une seule fois."""
    def __init__(self):
        super().__init__(
            _name="Garden",
            _image_path="assets/rooms/Garden.png",
            _gem_cost=1,
            _rarity=1,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.VERTE,
            _effet_texte="+1 gemme garantie (une seule fois), 30% de chance d'en gagner +1 supplémentaire."
        )

        self._used = False  #

        def garden_condition(r: int, c: int) -> bool:
            """Condition de placement : doit être sur les bords du manoir."""
            return c == 0 or c == 8  # en bordure
        self._placement_condition = garden_condition

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        """Effet unique : +1 gemme (garantie) et 30% de chance d’en obtenir une deuxième."""
        if self._used:
            return  # déjà utilisé → ne rien faire

        game.player.inventory.gems += 1  # gemme garantie
        if random.random() < 0.30:
            game.player.inventory.gems += 1  # bonus aléatoire

        self._used = True  



@dataclass
class Armory(Room):
    """Salle d'armurerie : clé + parfois un gros objet."""
    def __init__(self):
        super().__init__(
            _name="Armory",
            _image_path="assets/rooms/Armory.png",
            _gem_cost=1,
            _rarity=2,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.JAUNE,
            _effet_texte="Donne 1 clé et parfois un objet permanent (1 seule fois)."
        )
        self._gave_loot = False

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        if self._gave_loot:
            return

        # 100% : une clé
        game.player.inventory.keys += 1

        # 50% : un objet permanent dans la pièce
        if random.random() < 0.5:
            perm = random.choice([
                ShovelObj(), HammerObj(), LockpickKitObj(), MetalDetectorObj(), RabbitFootObj()
            ])
            cell = game.manor.cell(Coord(r, c))
            cell.room.contents.append(perm)

        self._gave_loot = True


@dataclass
class Library(Room):
    """Bibliothèque : +3 dé en entrant."""
    def __init__(self):
        super().__init__(
            _name="Library",
            _image_path="assets/rooms/Library.png",
            _gem_cost=2,
            _rarity=2,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.BLEUE,
            _effet_texte="+1 dé en entrant (une seule fois)."
        )
        self._used = False

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        if self._used:
            return ## retourne rien ou plutot fait rien
        game.player.inventory.dice += 3
        self._used = True


@dataclass
class Antechamber(Room):
    """Salle finale du manoir (objectif)."""
    def __init__(self):
        super().__init__(
            _name="Antechamber",
            _image_path="assets/rooms/exit.png",
            _gem_cost=0,
            _rarity=0,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.BLEUE,
            _effet_texte="Objectif accompli."
        )

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        pass


# ================================
#   ROOMS BONUS (modifs de tirage)
# ================================

@dataclass
class Furnace(Room):
    """Furnace : favorise salles riches, +10 or une seule fois et 5 clés, 7 gemmes mais enleve 2 pas a chauqe passage."""
    def __init__(self):
        super().__init__(
            _name="Furnace",
            _image_path="assets/rooms/Furnace.png",
            _gem_cost=0,
            _rarity=2,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.ROUGE,
            _effet_texte="Chaleur qui attire les trésors. +10 or (1 seule fois) mais perds 2 pas à chaque passage."
        )
        self.draw_modifiers = {"TreasureRoom": 1.6, "Armory": 1.3}
        self._gold_given = False

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        game.player.inventory.steps-=2
        if self._gold_given:
            return
        game.player.inventory.gold += 10
        game.player.inventory.keys+=5
        game.player.inventory.gems+=7
        self._gold_given = True


@dataclass
class Greenhouse(Room):
    """Greenhouse : favorise jardins et nourriture."""
    def __init__(self):
        super().__init__(
            _name="Greenhouse",
            _image_path="assets/rooms/Greenhouse.png",
            _gem_cost=1,
            _rarity=1,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.VERTE,
            _effet_texte="Donne 2 smalls business."
        )
        self.draw_modifiers = {"Garden": 2.0, "Pantry": 1.2}
        self.used = False

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        # Give 2 Small Business fragments on each entry
        if self.used :
            return
        try:
            game.player.inventory.add_small_business()
        except Exception:
            # defensive: if inventory lacks the method (older versions), silently ignore
            pass
        self.used = True


@dataclass
class Solarium(Room):
    """Solarium : favorise salles de savoir + donne 1 clé une fois."""
    def __init__(self):
        super().__init__(
            _name="Solarium",
            _image_path="assets/rooms/Solarium.png",
            _gem_cost=1,
            _rarity=1,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.VERTE,
            _effet_texte="Favorise Library. Donne 1 clé (1 fois)."
        )
        self.draw_modifiers = {"Library": 1.5, "PlainRoom": 1.2}
        self._gave_key = False

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        if self._gave_key:
            return
        game.player.inventory.keys += 1
        self._gave_key = True


@dataclass
class Veranda(Room):
    """Veranda : petite chance de gemme et influence sur les loots et la salle Garden.""" #ici on modifie la proba de cherccher de la nourriture apres passage dans chaque salle
    def __init__(self):
        super().__init__(
            _name="Veranda",
            _image_path="assets/rooms/Veranda.png",
            _gem_cost=0,
            _rarity=2,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.VERTE,
            _effet_texte=(
                "30% de chance de +1 gemme en entrant. "
                "Augmente les chances de nourriture de 60% pour les prochaines salles."
            )
        )
        #le TIRAGE DE SALLES, pas pour le loot
        self.draw_modifiers = {"Garden": 1.5}

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        # petit bonus immédiat
        if random.random() < 0.30:
            game.player.inventory.gems += 1

        # s'assurer que le dict existe (au cas où)
        if not hasattr(game, "temporary_loot_modifiers") or game.temporary_loot_modifiers is None:
            game.temporary_loot_modifiers = {}

        # 👉 ici on booste VIOLEMMENT la nourriture et le coffre
        # pour que tu le voies tout de suite dans la prochaine salle générée
        for obj_name in ("Apple", "Banana", "Cake", "Sandwich", "Meal", "Chest"):
            game.temporary_loot_modifiers[obj_name] = 1.5




@dataclass
class MaidsChamber(Room):
    """Maid's Chamber : chance d'un dé."""
    def __init__(self):
        super().__init__(
            _name="Maid's Chamber",
            _image_path="assets/rooms/MaidsChamber.png",
            _gem_cost=0,
            _rarity=1,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.ROUGE,
            _effet_texte="20% : +1 dé."
        )
        self.used=False

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        if self.used:
            return
        if random.random() < 0.20:
            game.player.inventory.dice += 1
        self.used=True
        


# ================================
#   Effets au TIRAGE (bonus table 2)
# ================================

@dataclass
class MasterBedroom(Room):
    """Quand elle est tirée : donne 1 clé."""
    def __init__(self):
        super().__init__(
            _name="Master Bedroom",
            _image_path="assets/rooms/bedroom.png",
            _gem_cost=1,
            _rarity=2,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.VIOLETTE,
            _effet_texte="Donne 1 clé quand elle apparaît dans les choix."
        )
        self._bonus_given = False

    def on_enter_default(self, game, r, c):
        if self._bonus_given:
            return
        game.player.inventory.keys += 1
        self._bonus_given = True



@dataclass
class WeightRoom(Room):
    """Quand elle est tirée : enlève la moitié des pas."""
    def __init__(self):
        super().__init__(
            _name="Weight Room",
            _image_path="assets/rooms/weightroom.png",
            _gem_cost=0,
            _rarity=1,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.ROUGE,
            _effet_texte="Au tirage : vous perdez la moitie de vos pas."
        )
        self._done = False

    def on_enter_default(self, game, r, c):
        """Effet appliqué uniquement la première fois que la salle est tirée."""
        if self._done:
            return
        game.player.inventory.steps = max(0, game.player.inventory.steps - game.player.inventory.steps//2)
        self._done = True



# -------------------------------------------------
# 1) Salle qui ajoute d'autres salles au catalogue
# -------------------------------------------------
@dataclass
class ChamberOfMirrors(Room):
    """
    Quand tu ENTRES dans cette salle pour la première fois,
    elle ajoute la salle PoolRoom au catalogue de tirage.
    """
    def __init__(self):
        super().__init__(
            _name="Chamber of Mirrors",
            _image_path="assets/rooms/Chamberofmirrors.png",
            _gem_cost=0,
            _rarity=2,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.VIOLETTE,
            _effet_texte="Ajoute 'Rumpus Room' au tirage (une seule fois)."
        )
        self._done = False

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        if self._done:
            return
        # on enregistre la room bonus pour les prochains tirages
        if RumpusRoom not in game.extra_room_classes:
            game.extra_room_classes.append(RumpusRoom)
        self._done = True


# -------------------------------------------------
# 2) La nouvelle salle qui devient disponible après
# -------------------------------------------------
@dataclass
class RumpusRoom(Room):
    """
    Petite salle bonus qu'on ne peut pas tirer au début,
    mais qu'on pourra tirer après être passé dans ChamberOfMirrors.
    """
    def __init__(self):
        super().__init__(
            _name="Pool Room",
            _image_path="assets/rooms/RumusRoom.png",
            _gem_cost=1,
            _rarity=1,
            _possible_doors={Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT},
            _couleur=CouleurPiece.BLEUE,
            _effet_texte="+8 golds en entrant (salle débloquée)."
            
        )
        self.used = False

    def on_enter_default(self, game: "Game", r: int, c: int) -> None:
        if self.used:
            return
        game.player.inventory.gold += 8
        self.used = True
