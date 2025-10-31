from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import random

# --- Imports du projet ---
from enums.direction import Direction
from enums.lock_level import LockLevel
from enums.room_colors import CouleurPiece

from models.coord import Coord
from models.door import Door
from world.manor import Manor
from actors.player import Player

# Rooms
from rooms.room_base import Room
from rooms.special_room import (
    Kitchen, Pantry, Garden, LockerRoom,
    TreasureRoom, Armory, Library, PlainRoom,
    EntranceHall, Antechamber
)

# Objets consommables
from objects.consumable import Apple, Banana, Cake, Sandwich, Meal

# Objets permanents (GAMEOBJECT)
from objects.permanent import ShovelObj, HammerObj, LockpickKitObj, MetalDetectorObj, RabbitFootObj

# Objets interactifs
from objects.interactive import Chest, DigSpot, Locker

# Enum des outils permanents
from items.permanent_item import PermanentItem

from models.room_deck_item import RoomDeckItem


# ========================
#  TABLES DE LOOT
# ========================
LOOT_TABLES = {
    "Chest": {
        "Key": 0.45,
        "Gold": 0.35,
        "Die": 0.10,
        "PermanentItem": 0.10,
    },
    "Digging": {
        "Empty": 0.30,
        "Gold": 0.30,
        "Key": 0.20,
        "Food": 0.15,
        "PermanentItem": 0.05,
    }
}


@dataclass
class Game:
    manor: Manor

    room_deck: List[RoomDeckItem] = field(default_factory=list)
    game_state: str = 'playing'
    current_draw_choices: List[Room] = field(default_factory=list)
    current_draw_target: Optional[Tuple[Coord, Direction]] = None

    def __post_init__(self):
        self.player = Player(self.manor.start)
        self.room_deck = self._initialize_room_deck()

        self.manor.cell(self.manor.start).room = self._get_and_remove_room_type(EntranceHall)
        self.manor.cell(self.manor.goal).room  = self._get_and_remove_room_type(Antechamber)

    # ========== PIERCHE ==========
    def _initialize_room_deck(self) -> List[RoomDeckItem]:
        all_room_definitions = self._get_all_room_definitions()
        return [RoomDeckItem(room=r) for r in all_room_definitions]

    def _get_and_remove_room_type(self, room_cls: type[Room]) -> Room:
        for item in self.room_deck:
            if item.is_in_deck and isinstance(item.room, room_cls):
                item.is_in_deck = False
                return item.room
        return room_cls()

    def _get_all_room_definitions(self) -> List[Room]:
        return [
            EntranceHall(),
            Antechamber(),
            PlainRoom(), PlainRoom(), PlainRoom(),
            Kitchen(), Pantry(), LockerRoom(),
            TreasureRoom(), Garden(), Armory(), Library(),
        ]

    # ========== TOOLS ==========
    def _has_tool_enum(self, enum_value: PermanentItem) -> bool:
        return enum_value in getattr(self.player.inventory, "tools", set())

    # ========== LOOT ==========
    def open_container_content(self, table_name: str) -> str:
        if table_name not in LOOT_TABLES:
            return "Erreur de loot."

        table = LOOT_TABLES[table_name]
        roll = random.random()
        cum = 0.0

        inv = self.player.inventory

        for loot, prob in table.items():
            cum += prob
            if roll <= cum:
                # TYPE DE LOOT
                if loot == "Empty":
                    return "C'est vide..."

                if loot == "Gold":
                    inv.gold += 1
                    return "Vous trouvez 1 pièce d'or."

                if loot == "Key":
                    inv.keys += 1
                    return "Vous trouvez une clé !"

                if loot == "Die":
                    inv.dice += 1
                    return "Vous trouvez un dé magique !"

                if loot == "Food":
                    room = self.manor.cell(self.player.pos).room
                    food = random.choice([Apple(), Banana(), Sandwich()])
                    room.contents.append(food)
                    return f"Vous trouvez {food.name}."

                if loot == "PermanentItem":
                    tool_enum = random.choice([
                        PermanentItem.SHOVEL,
                        PermanentItem.HAMMER,
                        PermanentItem.LOCKPICK,
                        PermanentItem.METAL_DETECTOR,
                        PermanentItem.RABBIT_FOOT
                    ])
                    inv.add_tool(tool_enum)
                    return f"Vous obtenez l'outil permanent : {tool_enum.name}"

        return "Vous ne trouvez rien."

    # ========== SPAWN OBJETS PAR SALLE ==========
    def spawn_objects_for_room(self, coord: Coord) -> None:
        cell = self.manor.cell(coord)
        room = cell.room
        if room is None: return
        if isinstance(room, (EntranceHall, Antechamber)): return

        # Loot spécifique par salle
        if isinstance(room, Kitchen):
            room.contents.append(random.choice([Apple(), Banana(), Cake(), Sandwich(), Meal()]))

        if isinstance(room, Pantry):
            room.contents.append(random.choice([Sandwich(), Meal()]))

        if isinstance(room, Garden):
            room.contents.append(DigSpot())

        if isinstance(room, LockerRoom):
            room.contents.append(Locker())

        if isinstance(room, TreasureRoom):
            room.contents.append(Chest())
            if random.random() < 0.5:
                room.contents.append(random.choice([
                    ShovelObj(), HammerObj(), LockpickKitObj(), MetalDetectorObj()
                ]))

        if isinstance(room, Armory):
            room.contents.append(random.choice([ShovelObj(), HammerObj(), LockpickKitObj(), MetalDetectorObj()]))

        if isinstance(room, Library):
            room.contents.append(random.choice([RabbitFootObj(), ShovelObj(), MetalDetectorObj(), Apple()]))

        # Bonus global RabbitFoot
        chest_chance = 0.2
        if self._has_tool_enum(PermanentItem.RABBIT_FOOT):
            chest_chance *= 1.3
        if random.random() < chest_chance:
            room.contents.append(Chest())

        # Bonus MetalDetector : chance directe de clé
        key_chance = 0.05
        if self._has_tool_enum(PermanentItem.METAL_DETECTOR):
            key_chance *= 2.0
        if random.random() < key_chance:
            self.player.inventory.keys += 1

        # PlainRoom bonus
        if isinstance(room, PlainRoom):
            if random.random() < 0.2:
                room.contents.append(random.choice([Apple(), Banana(), ShovelObj()]))

    # ========== CHOIX DES ROOMS ==========
    def draw_rooms(self, target_r: int, target_c: int, direction_from_cur: Direction) -> List[Room]:
        possible_items = []
        back_direction = direction_from_cur.opposite()

        for item in self.room_deck:
            room = item.room
            if not item.is_in_deck:
                continue
            if room.can_be_placed(target_r, target_c) and back_direction in getattr(room, 'possible_doors', set()):
                rarity = getattr(room, "rarity", 0)
                weight = 1 / (3 ** rarity)
                possible_items.append((item, weight))

        if not possible_items:
            return []

        k = min(3, len(possible_items))
        items, weights = zip(*possible_items)
        picks = random.choices(items, weights=weights, k=k)
        self.current_draw_choices = [it.room for it in picks]
        return self.current_draw_choices

    # ========== PLACER ROOM ==========
    def select_and_place_room(self, index: int) -> None:
        room = self.current_draw_choices[index]
        cur, d = self.current_draw_target
        nxt = Coord(cur.r + Direction.delta(d)[0], cur.c + Direction.delta(d)[1])

        self.player.inventory.gems -= getattr(room, "gem_cost", 0)

        for item in self.room_deck:
            if item.room is room:
                item.is_in_deck = False
                break

        lock = self.manor.cell(cur).doors[d].lock
        self.manor.cell(cur).doors[d] = Door(lock, nxt)

        back = d.opposite()
        self.manor.cell(nxt).room = room
        self.manor.cell(nxt).doors[back] = Door(LockLevel.UNLOCKED, cur)

        self.player.inventory.steps -= 1
        self.player.pos = nxt

        room.on_enter(self, nxt.r, nxt.c)
        self.spawn_objects_for_room(nxt)

        self.current_draw_choices = []
        self.current_draw_target = None
        self.game_state = "playing"
    # =====================================================
    # 🔥 INTERACTION OBJETS (Coffre / Casier / Spot)
    # =====================================================
    def interact_with_current_object(self):
        cell = self.manor.cell(self.player.pos)
        room = cell.room
        if not room or not room.contents:
            return "Rien à interagir ici."

        # On cible le premier objet interactif de la pièce
        for obj in list(room.contents):
            if hasattr(obj, "on_interact"):
                result = obj.on_interact(self)

                if getattr(obj, "consumed", False):
                    try:
                        room.contents.remove(obj)
                    except:
                        pass

                return result

        return "Aucun objet interactif ici."
