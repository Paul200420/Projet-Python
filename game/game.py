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

from rooms.room_base import Room
from rooms.special_room import (
    Kitchen, Pantry, Garden, LockerRoom,
    TreasureRoom, Armory, Library, PlainRoom,
    EntranceHall, Antechamber
)

from objects.consumable import Apple, Banana, Cake, Sandwich, Meal
from objects.permanent import ShovelObj, HammerObj, LockpickKitObj, MetalDetectorObj, RabbitFootObj
from objects.interactive import Chest, DigSpot, Locker

from models.room_deck_item import RoomDeckItem


# --- TABLES DE LOOT ---
LOOT_TABLES = {
    "Chest": {
        "Key": 0.45,
        "Gold": 0.35,
        "Die": 0.10,
        "PermanentItem_Random": 0.10,
    },
    "Digging": {
        "Empty": 0.30,
        "Gold": 0.30,
        "Key": 0.20,
        "Food_Steps": 0.15,
        "PermanentItem_Random": 0.05,
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

    # -------------------- Deck --------------------
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

    def _neighbor(self, coord: Coord, direction: Direction) -> Optional[Coord]:
        dr, dc = Direction.delta(direction)
        nxt = Coord(coord.r + dr, coord.c + dc)
        if not self.manor.in_bounds(nxt): return None
        return nxt

    def _has_tool_type(self, cls) -> bool:
        inv = self.player.inventory
        if hasattr(inv, "has_tool_type"):
            try: return inv.has_tool_type(cls)
            except: pass
        return any(isinstance(t, cls) for t in getattr(inv, "tools", set()))

    # ----------------- LOOT SYSTEM -----------------
    def open_container_content(self, container_type: str) -> str:
        table = LOOT_TABLES.get(container_type)
        if not table:
            return "Rien ici..."

        loot_types = list(table.keys())
        weights = list(table.values())
        selected = random.choices(loot_types, weights=weights, k=1)[0]
        inv = self.player.inventory

        # Vide
        if selected == "Empty":
            return "C'est vide..."

        # Or
        if selected == "Gold":
            amount = random.randint(10, 30)
            inv.gold += amount
            return f"Vous trouvez {amount} or !"

        # Clé
        if selected == "Key":
            inv.keys += 1
            return "Vous trouvez une clé !"

        # Dé
        if selected == "Die":
            inv.dice += 1
            return "Vous gagnez un dé !"

        # Nourriture → pas
        if selected == "Food_Steps":
            gain = 2 if random.random() < 0.5 else 1
            inv.steps += gain
            return f"Vous gagnez {gain} pas !"

        # Objet permanent aléatoire
        if selected == "PermanentItem_Random":
            candidates = [ShovelObj, HammerObj, LockpickKitObj, MetalDetectorObj, RabbitFootObj]
            tool_cls = random.choice(candidates)
            if hasattr(inv, "has_tool_type") and inv.has_tool_type(tool_cls):
                return f"Vous trouvez {tool_cls.__name__}, mais vous l'avez déjà."
            inv.add_tool(tool_cls())
            return f"Objet permanent obtenu : {tool_cls.__name__} !"

        return "Vous trouvez quelque chose..."

    # ----------------- OBJETS -----------------
    def spawn_objects_for_room(self, coord: Coord) -> None:
        cell = self.manor.cell(coord)
        room = cell.room
        if room is None or isinstance(room, (EntranceHall, Antechamber)): return

        if isinstance(room, Kitchen):
            room.contents.append(random.choice([Apple(), Banana(), Cake(), Sandwich(), Meal()]))
        elif isinstance(room, Pantry):
            room.contents.append(random.choice([Sandwich(), Meal()]))
        elif isinstance(room, Garden):
            room.contents.append(DigSpot())
        elif isinstance(room, LockerRoom):
            room.contents.append(Locker())
        elif isinstance(room, TreasureRoom):
            room.contents.append(Chest())
            if random.random() < 0.5:
                room.contents.append(random.choice([ShovelObj(), HammerObj(), LockpickKitObj(), MetalDetectorObj()]))
        elif isinstance(room, Armory):
            room.contents.append(random.choice([ShovelObj(), HammerObj(), LockpickKitObj(), MetalDetectorObj()]))
        elif isinstance(room, Library):
            room.contents.append(random.choice([RabbitFootObj(), ShovelObj(), MetalDetectorObj(), Apple()]))

        # Effets globaux
        if random.random() < (0.26 if self._has_tool_type(RabbitFootObj) else 0.20):
            room.contents.append(Chest())

        if random.random() < (0.10 if self._has_tool_type(MetalDetectorObj) else 0.05):
            self.player.inventory.keys += 1

        if isinstance(room, PlainRoom) and random.random() < 0.2:
            room.contents.append(random.choice([Apple(), Banana(), ShovelObj()]))

    # ----------------- PIÈCES & PLACEMENT -----------------
    def _get_draw_modifier(self, room: Room) -> float:
        modifier = 1.0
        current_room = self.manor.cell(self.player.pos).room
        if current_room and getattr(current_room, "name", "") == "Greenhouse" \
           and getattr(room, "couleur", None) == CouleurPiece.VERTE:
            modifier *= 2.0
        return modifier

    def draw_rooms(self, target_r: int, target_c: int, direction_from_cur: Direction) -> List[Room]:
        possible_items = []
        back = direction_from_cur.opposite()

        for item in self.room_deck:
            room = item.room
            if not item.is_in_deck: continue
            if room.can_be_placed(target_r, target_c) and back in room.possible_doors:
                possible_items.append({'item': item, 'modifier': self._get_draw_modifier(room)})

        if not possible_items: return []

        items = [it['item'] for it in possible_items]
        weights = [(1 / (3 ** it['item'].room.rarity)) * it['modifier'] for it in possible_items]
        k = min(3, len(items))

        choices = random.choices(items, weights=weights, k=k)
        rooms = [it.room for it in choices]

        if not any(r.gem_cost == 0 for r in rooms):
            free_items = [it for it in self.room_deck if it.is_in_deck and it.room.gem_cost == 0]
            if free_items:
                worst = max(choices, key=lambda it: it.room.gem_cost + it.room.rarity * 5)
                choices.remove(worst)
                choices.append(random.choice(free_items))

        self.current_draw_choices = [it.room for it in choices]
        return self.current_draw_choices

    def reroll_draw_choices(self) -> bool:
        if self.player.inventory.dice >= 1 and self.current_draw_target:
            self.player.inventory.dice -= 1
            cur, d = self.current_draw_target
            nxt = self._neighbor(cur, d)
            if nxt: self.current_draw_choices = self.draw_rooms(nxt.r, nxt.c, d)
            return True
        return False

    def select_and_place_room(self, chosen_room_index: int) -> None:
        room = self.current_draw_choices[chosen_room_index]
        cur, d = self.current_draw_target
        nxt = self._neighbor(cur, d)

        self.player.inventory.gems -= room.gem_cost
        for item in self.room_deck:
            if item.room is room:
                item.is_in_deck = False
                break

        lock = self.manor.cell(cur).doors.get(d, Door()).lock
        self.manor.cell(cur).doors[d] = Door(_lock=lock, _leads_to=nxt)
        self.manor.cell(nxt).room = room
        self.manor.cell(nxt).doors[d.opposite()] = Door(_lock=LockLevel.UNLOCKED, _leads_to=cur)

        self.player.inventory.steps -= 1
        self.player.pos = nxt
        room.on_enter(self, nxt.r, nxt.c)
        self.spawn_objects_for_room(nxt)

        self.current_draw_choices = []
        self.current_draw_target = None
        self.game_state = 'playing'

    # ---------------- Déplacement ----------------
    def open_or_place(self, d: Direction) -> bool:
        cur = self.player.pos
        nxt = self._neighbor(cur, d)
        if nxt is None: return False
        tgt = self.manor.cell(nxt)
        cur_cell = self.manor.cell(cur)

        if tgt.room is not None:
            return False

        if d not in cur_cell.doors:
            cur_cell.doors[d] = Door(_lock=self._random_lock_for_row(nxt.r), _leads_to=nxt)

        door = cur_cell.doors[d]
        if door.can_open(self.player.inventory):
            door.open(self.player.inventory)
            self.current_draw_target = (cur, d)
            self.current_draw_choices = self.draw_rooms(nxt.r, nxt.c, d)

            if not self.current_draw_choices:
                self.game_state = 'lost_blocked'
                return False

            self.game_state = 'drawing_room'
            return True
        return False

    def move(self, d: Direction) -> bool:
        cur_cell = self.manor.cell(self.player.pos)
        door = cur_cell.doors.get(d)
        if not door or door.lock != LockLevel.UNLOCKED: return False
        if self.player.inventory.steps <= 0: return False

        self.player.inventory.steps -= 1
        self.player.pos = door.leads_to

        new_cell = self.manor.cell(self.player.pos)
        if new_cell.room:
            new_cell.room.on_enter(self, self.player.pos.r, self.player.pos.c)
        return True

    def reached_exit(self) -> bool:
        return self.player.pos == self.manor.goal

    # ---------------- Locks par étage ----------------
    def _random_lock_for_row(self, row: int) -> LockLevel:
        row = max(0, min(self.manor.rows - 1, row))
        if row == self.manor.rows - 1: return LockLevel.UNLOCKED
        if row == 0: return LockLevel.DOUBLE_LOCKED

        p = random.random()
        return (
            LockLevel.UNLOCKED if (row == 3 and p < 0.7) or (row == 2 and p < 0.4) or (row == 1 and p < 0.2)
            else LockLevel.LOCKED if (row == 3 or (row == 2 and p < 0.9) or (row == 1 and p < 0.7))
            else LockLevel.DOUBLE_LOCKED
        )

    def _unlock_both_sides(self, from_coord: Coord, d: Direction) -> None:
        cur_cell = self.manor.cell(from_coord)
        door = cur_cell.doors.get(d)
        if not door: return
        door.lock = LockLevel.UNLOCKED

        twin = self.manor.cell(door.leads_to).doors.get(d.opposite())
        if twin: twin.lock = LockLevel.UNLOCKED
