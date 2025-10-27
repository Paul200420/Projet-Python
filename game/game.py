from __future__ import annotations
from dataclasses import dataclass
from enums.direction import Direction
from enums.lock_level import LockLevel
from models.coord import Coord
from models.door import Door
from world.manor import Manor
from actors.player import Player
# from rooms.room_types import EntryRoom, ExitRoom
import random

from rooms.special_rooms import (
    Kitchen, Pantry, Garden, LockerRoom,
    TreasureRoom, Armory, Library, PlainRoom,
    EntranceHall, Antechamber
)
from objects.consumable import Apple, Banana, Cake, Sandwich, Meal
from objects.permanent import ShovelObj, HammerObj, LockpickKitObj, MetalDetectorObj, RabbitFootObj
from objects.interactive import Chest, DigSpot, Locker

@dataclass
class Game:
    manor: Manor
 
    def __post_init__(self):
        self.player = Player(self.manor.start)
        # Place les rooms de base
        # self.manor.cell(self.manor.start).room = EntryRoom()
        self.manor.cell(self.manor.start).room = EntranceHall()
        

        # self.manor.cell(self.manor.goal).room = ExitRoom()
        self.manor.cell(self.manor.goal).room = Antechamber()

    # --- outils internes ---
    # def _neighbor(self, coord: Coord, d: Direction) -> Coord | None:
    #     dr, dc = Direction.delta(d)
    #     nxt = Coord(coord.r + dr, coord.c + dc)
    #     return nxt if self.manor.in_bounds(nxt) else None

    def _neighbor(self, coord, direction):
        dr, dc = Direction.delta(direction)
        nxt = Coord(coord.r + dr, coord.c + dc)
        if not self.manor.in_bounds(nxt):
            return None  # <-- IMPORTANT : retourne None si hors manoir
        return nxt
    
    def spawn_objects_for_room(self, coord):
    # """Place automatiquement des objets dans une salle selon son type."""
        cell = self.manor.cell(coord)
        room = cell.room
        if room is None:
            return  # sécurité

        # 🎯 Aucune apparition dans ces salles
        if isinstance(room, (EntranceHall, Antechamber)):
            return

        # =============================
        # 🧑‍🍳 SALLES DE NOURRITURE
        # =============================
        if isinstance(room, Kitchen):
            # Beaucoup de nourriture
            room.contents.append(random.choice([Apple(), Banana(), Cake(), Sandwich(), Meal()]))

        elif isinstance(room, Pantry):
            # Nourriture puissante uniquement
            room.contents.append(random.choice([Sandwich(), Meal()]))

        # =============================
        # 🌿 SALLES EXTÉRIEURES
        # =============================
        elif isinstance(room, Garden):
            room.contents.append(DigSpot())

        # =============================
        # 🔒 SALLES À CASIERS
        # =============================
        elif isinstance(room, LockerRoom):
            room.contents.append(Locker())

        # =============================
        # 💎 SALLE TRÉSOR
        # =============================
        elif isinstance(room, TreasureRoom):
            # Un coffre obligatoire
            room.contents.append(Chest())
            # Parfois un objet permanent en plus
            if random.random() < 0.5:
                room.contents.append(random.choice([ShovelObj(), HammerObj(), LockpickKitObj(), MetalDetectorObj()]))

        # =============================
        # ⚔️ ARMORY
        # =============================
        elif isinstance(room, Armory):
            room.contents.append(random.choice([ShovelObj(), HammerObj(), LockpickKitObj(), MetalDetectorObj()]))

        # =============================
        # 📚 LIBRARY
        # =============================
        elif isinstance(room, Library):
            # Objets de chance ou rares
            room.contents.append(random.choice([RabbitFootObj(), ShovelObj(), MetalDetectorObj(), Apple()]))

        # =============================
        # 🧱 Plain Room
        # =============================
        elif isinstance(room, PlainRoom):
            # 20% de chance d'avoir un objet
            if random.random() < 0.2:
                room.contents.append(random.choice([Apple(), Banana(), ShovelObj()]))

        # sinon ne rien faire (salle vide)

    def generate_random_room(self, r: int, c: int):
            """Génère une salle aléatoire en tenant compte de la rareté et des conditions."""
            possible_rooms = [
                PlainRoom(),
                Kitchen(),
                Pantry(),
                LockerRoom(),
                TreasureRoom(),
                Garden(),
                Armory(),
                Library()
            ]

            # Filtrer les salles selon les conditions de placement
            filtered_rooms = [room for room in possible_rooms if room.can_be_placed(r, c)]

            # Vérifier si le joueur a assez de gemmes
            filtered_rooms = [room for room in filtered_rooms 
                            if self.player.inventory.gems >= room.gem_cost]

            if not filtered_rooms:
                return PlainRoom()  # Salle par défaut si aucune option possible

            # Calculer les poids en fonction de la rareté
            # La formule est: poids = base_weight * (1/3)^rarity
            weights = [pow(1/3, room.rarity) for room in filtered_rooms]

            return random.choices(filtered_rooms, weights=weights, k=1)[0]
        
    
    
    
    
    
    # --- actions de base ---
    def open_or_place(self, d: Direction) -> bool:
        """
        Ouvre/pose une salle adjacente dans la direction d, si possible.
        - Vérifie le coût en gemmes et les conditions de placement
        - Ne crée que les portes autorisées par la salle
        - Crée des portes bidirectionnelles UNLOCKED
        """
        cur = self.player.pos
        nxt = self._neighbor(cur, d)
        if nxt is None:
            return False

        # Place la salle si absente
        tgt_cell = self.manor.cell(nxt)
        if tgt_cell.room is None:
            # Générer une salle aléatoire appropriée
            room = self.generate_random_room(nxt.r, nxt.c)
            
            # Vérifier si la direction demandée est possible pour cette salle
            if d not in room.possible_doors:
                return False

            # Vérifier et déduire le coût en gemmes
            if self.player.inventory.gems < room.gem_cost:
                return False
            self.player.inventory.gems -= room.gem_cost

            # Placer la salle et ses objets
            tgt_cell.room = room
            self.spawn_objects_for_room(nxt)

        # Crée la porte aller si autorisée
        cur_cell = self.manor.cell(cur)
        if d not in cur_cell.doors:
            cur_cell.doors[d] = Door(_lock=LockLevel.UNLOCKED, _leads_to=nxt)

        # Crée la porte retour si autorisée
        back = {Direction.UP: Direction.DOWN, Direction.DOWN: Direction.UP,
                Direction.LEFT: Direction.RIGHT, Direction.RIGHT: Direction.LEFT}[d]
        if back not in tgt_cell.doors and back in tgt_cell.room.possible_doors:
            tgt_cell.doors[back] = Door(_lock=LockLevel.UNLOCKED, _leads_to=cur)

        return True

    def move(self, d: Direction) -> bool:
        """Se déplacer via une porte ouverte; consomme 1 step."""
        cur_cell = self.manor.cell(self.player.pos)
        door = cur_cell.doors.get(d)
        if not door:
            return False
        if not door.can_open(self.player.inventory):
            return False
        if not door.open(self.player.inventory):
            return False
        # Consomme 1 pas
        if self.player.inventory.steps <= 0:
            return False
        self.player.inventory.steps -= 1
        # Déplacement
        self.player.pos = door.leads_to
        # Hook d'entrée
        new_cell = self.manor.cell(self.player.pos)
        if new_cell.room:
            new_cell.room.on_enter(self, self.player.pos.r, self.player.pos.c)
        return True

    def reached_exit(self) -> bool:
        return self.player.pos == self.manor.goal
    # --- helpers objets ---
    def place_object_at(self, coord, obj) -> bool:
        """Place un objet dans la room à coord. Retourne False si pas de room."""
        if not self.manor.in_bounds(coord):
            return False
        cell = self.manor.cell(coord)
        if cell.room is None:
            return False
        cell.room.contents.append(obj)
        return True

    def pick_up_here(self) -> str | None:
        """Interagit avec le premier objet de la room du joueur; retire s'il est consommé."""
        cell = self.manor.cell(self.player.pos)
        if not cell.room or not cell.room.contents:
            return None
        obj = cell.room.contents[0]
        msg = obj.on_interact(self)
        if getattr(obj, "consumed", False):
            cell.room.contents.pop(0)
        return msg
