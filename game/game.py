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

# Objets dans les rooms (spawn)
from objects.consumable import Apple, Banana, Cake, Sandwich, Meal
from objects.permanent import ShovelObj, HammerObj, LockpickKitObj, MetalDetectorObj, RabbitFootObj
from objects.interactive import Chest, DigSpot, Locker

# Deck
from models.room_deck_item import RoomDeckItem

# Enum des outils stockés dans l'inventaire
from items.permanent_item import PermanentItem


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
    },
    # Décommente si tu veux un loot spécifique pour les casiers :
    # "Locker": {
    #     "Empty": 0.25,
    #     "Key": 0.35,
    #     "Gold": 0.20,
    #     "Die": 0.10,
    #     "PermanentItem_Random": 0.10,
    # }
}


@dataclass
class Game:
    manor: Manor

    # État du jeu
    room_deck: List[RoomDeckItem] = field(default_factory=list)
    game_state: str = 'playing'
    current_draw_choices: List[Room] = field(default_factory=list)
    current_draw_target: Optional[Tuple[Coord, Direction]] = None

    def __post_init__(self):
        self.player = Player(self.manor.start)

        # Init deck et placement des rooms fixes
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
        return room_cls()  # fallback sûr

    def _get_all_room_definitions(self) -> List[Room]:
        return [
            EntranceHall(),
            Antechamber(),
            PlainRoom(), PlainRoom(), PlainRoom(),
            Kitchen(), Pantry(), LockerRoom(),
            TreasureRoom(), Garden(), Armory(), Library(),
        ]

    # ----------------- Utils -----------------
    def _neighbor(self, coord: Coord, direction: Direction) -> Optional[Coord]:
        dr, dc = Direction.delta(direction)
        nxt = Coord(coord.r + dr, coord.c + dc)
        if not self.manor.in_bounds(nxt):
            return None
        return nxt

    # ----------------- LOOT SYSTEM -----------------
    def open_container_content(self, container_type: str) -> str:
        """
        Tire et applique le butin pour un conteneur (Chest / Digging / Locker si ajouté).
        Met à jour l'inventaire et renvoie un message utilisateur.
        """
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
            inv.gold = inv.gold + amount
            return f"Vous trouvez {amount} or !"

        # Clé
        if selected == "Key":
            inv.keys = inv.keys + 1
            return "Vous trouvez une clé !"

        # Dé (bonus de relance)
        if selected == "Die":
            inv.dice = inv.dice + 1
            return "Vous gagnez un dé !"

        # Nourriture -> pas
        if selected == "Food_Steps":
            gain = 2 if random.random() < 0.5 else 1
            inv.steps = inv.steps + gain
            return f"Vous gagnez {gain} pas !"

        # Objet permanent aléatoire (Enum PermanentItem dans inventory.tools)
        if selected == "PermanentItem_Random":
            candidates = [
                PermanentItem.SHOVEL,
                PermanentItem.HAMMER,
                PermanentItem.LOCKPICK_KIT,
                PermanentItem.METAL_DETECTOR,
                PermanentItem.RABBIT_FOOT,
            ]
            tool_enum = random.choice(candidates)
            if tool_enum in inv.tools:
                return f"Vous trouvez {tool_enum.name}, mais vous l'avez déjà."
            inv.add_tool(tool_enum)
            return f"Objet permanent obtenu : {tool_enum.name} !"

        return "Vous trouvez quelque chose..."

    # ----------------- OBJETS (spawn) -----------------
    def spawn_objects_for_room(self, coord: Coord) -> None:
        cell = self.manor.cell(coord)
        room = cell.room
        if room is None or isinstance(room, (EntranceHall, Antechamber)):
            return

        # Contenu spécifique par type de salle
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

        # --- Effets globaux influencés par les outils permanents (Enum dans inventory.tools) ---
        # 1) Patte de lapin -> +coffres
        base_chest_chance = 0.20
        if PermanentItem.RABBIT_FOOT in self.player.inventory.tools:
            base_chest_chance *= 1.3
        if random.random() < base_chest_chance:
            room.contents.append(Chest())

        # 2) Détecteur de métaux -> chance de gagner une clé directement
        base_key_chance = 0.05
        if PermanentItem.METAL_DETECTOR in self.player.inventory.tools:
            base_key_chance *= 2.0
        if random.random() < base_key_chance:
            self.player.inventory.keys = self.player.inventory.keys + 1

        # 3) Bonus PlainRoom
        if isinstance(room, PlainRoom) and random.random() < 0.2:
            room.contents.append(random.choice([Apple(), Banana(), ShovelObj()]))

    # ----------------- Tirage & Placement -----------------
    def _get_draw_modifier(self, room: Room) -> float:
        """Ex: Greenhouse double les rooms vertes (si tu ajoutes la Room correspondante)."""
        modifier = 1.0
        current_room = self.manor.cell(self.player.pos).room
        try:
            if current_room and getattr(current_room, "name", "") == "Greenhouse" \
               and getattr(room, "couleur", None) == CouleurPiece.VERTE:
                modifier *= 2.0
        except Exception:
            pass
        return modifier

    def draw_rooms(self, target_r: int, target_c: int, direction_from_cur: Direction) -> List[Room]:
        """Tire jusqu'à 3 pièces de la pioche en respectant rareté / portes / placement."""
        possible_items: List[dict] = []
        back = direction_from_cur.opposite()

        for item in self.room_deck:
            room = item.room
            if not item.is_in_deck:
                continue
            if room.can_be_placed(target_r, target_c) and back in getattr(room, 'possible_doors', set()):
                possible_items.append({'item': item, 'modifier': self._get_draw_modifier(room)})

        if not possible_items:
            return []

        items = [it['item'] for it in possible_items]
        weights = [(1 / (3 ** getattr(it['item'].room, 'rarity', 0))) * it['modifier'] for it in possible_items]
        k = min(3, len(items))

        choices = random.choices(items, weights=weights, k=k)
        chosen_rooms = [it.room for it in choices]

        # Garantie : au moins une room gratuite
        if not any(getattr(r, 'gem_cost', 0) == 0 for r in chosen_rooms):
            free_items = [it for it in self.room_deck
                          if it.is_in_deck and getattr(it.room, 'gem_cost', 0) == 0 and it not in choices]
            if free_items:
                worst = max(
                    choices,
                    key=lambda it: getattr(it.room, 'gem_cost', 0) + getattr(it.room, 'rarity', 0) * 5
                )
                choices.remove(worst)
                choices.append(random.choice(free_items))

        self.current_draw_choices = [it.room for it in choices]
        return self.current_draw_choices

    def reroll_draw_choices(self) -> bool:
        """Dépense 1 dé pour relancer le tirage."""
        if self.player.inventory.dice >= 1 and self.current_draw_target is not None:
            self.player.inventory.dice -= 1
            cur, d = self.current_draw_target
            nxt = self._neighbor(cur, d)
            if nxt is None:
                return False
            self.current_draw_choices = self.draw_rooms(nxt.r, nxt.c, d)
            return True
        return False

    def select_and_place_room(self, chosen_room_index: int) -> None:
        """Paie, place la room choisie, connecte les portes, avance le joueur et applique les effets."""
        room = self.current_draw_choices[chosen_room_index]
        cur, d = self.current_draw_target  # type: ignore[misc]
        nxt = self._neighbor(cur, d)
        assert nxt is not None, "Case cible hors limites."

        # 1) Payer
        self.player.inventory.gems = self.player.inventory.gems - getattr(room, 'gem_cost', 0)

        # 2) Marquer la room comme utilisée
        for item in self.room_deck:
            if item.room is room:
                item.is_in_deck = False
                break

        # 3) Placer + portes
        lock_level = self.manor.cell(cur).doors.get(d, Door()).lock
        self.manor.cell(cur).doors[d] = Door(_lock=lock_level, _leads_to=nxt)

        back = d.opposite()
        self.manor.cell(nxt).room = room
        self.manor.cell(nxt).doors[back] = Door(_lock=LockLevel.UNLOCKED, _leads_to=cur)

        # 4) Avancer (1 step)
        if self.player.inventory.steps > 0:
            self.player.inventory.steps -= 1
        self.player.pos = nxt

        # 5) Effet d'entrée + objets
        room.on_enter(self, nxt.r, nxt.c)
        self.spawn_objects_for_room(nxt)

        # 6) Reset
        self.current_draw_choices = []
        self.current_draw_target = None
        self.game_state = 'playing'

    # ---------------- Déplacement ----------------
    def open_or_place(self, d: Direction) -> bool:
        """Ouvrir/poser une room dans la direction d."""
        cur = self.player.pos
        nxt = self._neighbor(cur, d)
        if nxt is None:
            return False

        tgt = self.manor.cell(nxt)
        cur_cell = self.manor.cell(cur)

        # Déjà une room -> rien à faire ici
        if tgt.room is not None:
            return False

        # Assigner un lock si absent
        if d not in cur_cell.doors:
            cur_cell.doors[d] = Door(_lock=self._random_lock_for_row(nxt.r), _leads_to=nxt)

        door = cur_cell.doors[d]
        if door.can_open(self.player.inventory):
            # consomme clé/lockpick si nécessaire
            door.open(self.player.inventory)

            # Tirage
            self.current_draw_target = (cur, d)
            self.current_draw_choices = self.draw_rooms(nxt.r, nxt.c, d)

            if not self.current_draw_choices:
                self.game_state = 'lost_blocked'
                return False

            self.game_state = 'drawing_room'
            return True
        else:
            return False

    def move(self, d: Direction) -> bool:
        """Se déplacer via une porte déjà UNLOCKED (coûte 1 step)."""
        cur_cell = self.manor.cell(self.player.pos)
        door = cur_cell.doors.get(d)
        if not door or door.lock != LockLevel.UNLOCKED:
            return False
        if self.player.inventory.steps <= 0:
            return False

        self.player.inventory.steps -= 1
        self.player.pos = door.leads_to

        new_cell = self.manor.cell(self.player.pos)
        if new_cell.room:
            new_cell.room.on_enter(self, self.player.pos.r, self.player.pos.c)
        return True

    def reached_exit(self) -> bool:
        return self.player.pos == self.manor.goal

    # ---------------- Locks par “étage” (rangée) ----------------
    def _random_lock_for_row(self, row: int) -> LockLevel:
        row = max(0, min(self.manor.rows - 1, row))

        if row == self.manor.rows - 1:
            return LockLevel.UNLOCKED
        if row == 0:
            return LockLevel.DOUBLE_LOCKED

        # distributions comme dans ta version
        if row == 3:
            p = random.random()
            return LockLevel.UNLOCKED if p < 0.70 else LockLevel.LOCKED

        if row == 2:
            p = random.random()
            if p < 0.40: return LockLevel.UNLOCKED
            if p < 0.90: return LockLevel.LOCKED
            return LockLevel.DOUBLE_LOCKED

        if row == 1:
            p = random.random()
            if p < 0.20: return LockLevel.UNLOCKED
            if p < 0.70: return LockLevel.LOCKED
            return LockLevel.DOUBLE_LOCKED

        return LockLevel.UNLOCKED

    def _unlock_both_sides(self, from_coord: Coord, d: Direction) -> None:
        """Met la porte traversée ET sa jumelle en UNLOCKED."""
        cur_cell = self.manor.cell(from_coord)
        door = cur_cell.doors.get(d)
        if not door:
            return
        door.lock = LockLevel.UNLOCKED

        back = d.opposite()
        tgt_cell = self.manor.cell(door.leads_to)
        twin = tgt_cell.doors.get(back)
        if twin:
            twin.lock = LockLevel.UNLOCKED
