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

# Classe de base + rooms concrètes (aligné avec tes fichiers)
from rooms.room_base import Room
from rooms.special_room import (
    Kitchen, Pantry, Garden, LockerRoom,
    TreasureRoom, Armory, Library, PlainRoom,
    EntranceHall, Antechamber
)

# Objets
from objects.consumable import Apple, Banana, Cake, Sandwich, Meal
from objects.permanent import ShovelObj, HammerObj, LockpickKitObj, MetalDetectorObj, RabbitFootObj
from objects.interactive import Chest, DigSpot, Locker

# Élément de pioche
from models.room_deck_item import RoomDeckItem


# --- CONSTANTES DE JEUX (Section 2.8) ---
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
# -------------------------------------------


@dataclass
class Game:
    manor: Manor

    # --- État de jeu (Section 2.7) ---
    room_deck: List[RoomDeckItem] = field(default_factory=list)
    game_state: str = 'playing'
    current_draw_choices: List[Room] = field(default_factory=list)
    current_draw_target: Optional[Tuple[Coord, Direction]] = None

    def __post_init__(self):
        self.player = Player(self.manor.start)

        # Initialisation de la pioche
        self.room_deck = self._initialize_room_deck()

        # Placer les rooms fixes et les retirer du deck
        self.manor.cell(self.manor.start).room = self._get_and_remove_room_type(EntranceHall)
        self.manor.cell(self.manor.goal).room  = self._get_and_remove_room_type(Antechamber)

    # --- Deck / Pioche ---
    def _initialize_room_deck(self) -> List[RoomDeckItem]:
        """Crée la pioche complète en encapsulant chaque Room."""
        all_room_definitions = self._get_all_room_definitions()
        return [RoomDeckItem(room=r) for r in all_room_definitions]

    def _get_and_remove_room_type(self, room_cls: type[Room]) -> Room:
        """Récupère une Room par TYPE dans la pioche et la marque comme utilisée."""
        for item in self.room_deck:
            if item.is_in_deck and isinstance(item.room, room_cls):
                item.is_in_deck = False
                return item.room
        # Fallback sûr (ne devrait pas arriver si la liste est bien construite)
        return room_cls()

    def _get_all_room_definitions(self) -> List[Room]:
        """
        Liste complète des pièces (ne passe pas d'arguments aux constructeurs,
        tes classes fixent déjà leurs propriétés en interne).
        """
        return [
            EntranceHall(),
            Antechamber(),
            PlainRoom(), PlainRoom(), PlainRoom(),
            Kitchen(), Pantry(), LockerRoom(),
            TreasureRoom(), Garden(), Armory(), Library(),
            # Ajoute ici d’autres rooms si tu en crées
        ]

    # --- Outils internes ---
    def _neighbor(self, coord: Coord, direction: Direction) -> Optional[Coord]:
        dr, dc = Direction.delta(direction)
        nxt = Coord(coord.r + dr, coord.c + dc)
        if not self.manor.in_bounds(nxt):
            return None
        return nxt

    # --- Butin (Section 2.8) : à brancher plus tard ---
    def open_container_content(self, container_type: str) -> List['GameObject']:
        """Tire aléatoirement le contenu d'un conteneur. (Actuellement non branché pour éviter les erreurs)"""
        if container_type not in LOOT_TABLES:
            return []
        # À implémenter si tes coffres/trous appellent cette méthode.
        return []

    # --- Apparition des objets selon la room ---
    def spawn_objects_for_room(self, coord: Coord) -> None:
        cell = self.manor.cell(coord)
        room = cell.room
        if room is None:
            return

        # Pas d’objets dans ces rooms fixes
        if isinstance(room, (EntranceHall, Antechamber)):
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

        # --- Effets globaux (Patte de lapin / Détecteur de métaux) ---
        # Chance de coffre (Patte de lapin ↑)
        base_chest_chance = 0.20
        if self.player.inventory.has_tool_type(RabbitFootObj):
            base_chest_chance *= 1.3
        if random.random() < base_chest_chance:
            room.contents.append(Chest())

        # Chance de trouver une clé (Détecteur ↑)
        base_key_chance = 0.05
        if self.player.inventory.has_tool_type(MetalDetectorObj):
            base_key_chance *= 2.0
        if random.random() < base_key_chance:
            # Créditer directement l’inventaire (simple et fiable)
            self.player.inventory.keys = self.player.inventory.keys + 1

        # Petit bonus pour PlainRoom
        if isinstance(room, PlainRoom):
            if random.random() < 0.2:
                room.contents.append(random.choice([Apple(), Banana(), ShovelObj()]))

    # --- Tirage & Rarete (Section 2.7) ---
    def _get_draw_modifier(self, room: Room) -> float:
        """Calcule un modificateur de tirage (ex: Greenhouse double les rooms vertes)."""
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
        """Tire jusqu'à 3 pièces de la pioche en respectant les règles (Section 2.7)."""
        possible_items: List[dict] = []
        back_direction = direction_from_cur.opposite()

        for item in self.room_deck:
            room = item.room
            if not item.is_in_deck:
                continue
            # Vérifie placement + présence de la porte retour
            if room.can_be_placed(target_r, target_c) and back_direction in getattr(room, 'possible_doors', set()):
                modifier = self._get_draw_modifier(room)
                possible_items.append({'item': item, 'modifier': modifier})

        if len(possible_items) == 0:
            return []

        # Pondération : (1 / (3 ** rarity)) * modifier
        items_list = [it['item'] for it in possible_items]
        weights = [(1 / (3 ** getattr(it['item'].room, 'rarity', 0))) * it['modifier'] for it in possible_items]
        k = min(3, len(items_list))

        # Tirage (peut contenir des doublons, acceptable pour un premier jet)
        choices = random.choices(items_list, weights=weights, k=k)
        choices_rooms = [it.room for it in choices]

        # Garantie d'avoir au moins une room gratuite
        if not any(getattr(rm, 'gem_cost', 0) == 0 for rm in choices_rooms):
            free_items_in_deck = [
                it for it in self.room_deck
                if it.is_in_deck and getattr(it.room, 'gem_cost', 0) == 0 and it not in choices
            ]
            if free_items_in_deck:
                item_to_replace = max(
                    choices,
                    key=lambda it: getattr(it.room, 'gem_cost', 0) + getattr(it.room, 'rarity', 0) * 5
                )
                choices.remove(item_to_replace)
                choices.append(random.choice(free_items_in_deck))

        self.current_draw_choices = [it.room for it in choices]
        return self.current_draw_choices

    def reroll_draw_choices(self) -> bool:
        """Dépense un dé pour relancer le tirage (Section 2.7)."""
        if self.player.inventory.dice >= 1 and self.current_draw_target is not None:
            self.player.inventory.dice -= 1
            cur_pos, d = self.current_draw_target
            nxt_pos = self._neighbor(cur_pos, d)
            if nxt_pos is None:
                return False
            self.current_draw_choices = self.draw_rooms(nxt_pos.r, nxt_pos.c, d)
            return True
        return False

    def select_and_place_room(self, chosen_room_index: int) -> None:
        """Paie, place la pièce, connecte les portes, déplace le joueur, applique les effets."""
        room = self.current_draw_choices[chosen_room_index]
        cur_pos, d = self.current_draw_target  # type: ignore[misc]
        nxt_pos = self._neighbor(cur_pos, d)
        assert nxt_pos is not None, "Case cible hors limites."

        # 1. Dépense des gemmes
        self.player.inventory.gems = self.player.inventory.gems - getattr(room, 'gem_cost', 0)

        # 2. Marquer la pièce comme utilisée
        for item in self.room_deck:
            if item.room is room:
                item.is_in_deck = False
                break

        # 3. Placement et portes
        # Conserver le niveau de verrou déjà attribué pour cette porte (ou UNLOCKED par défaut)
        lock_level = self.manor.cell(cur_pos).doors.get(d, Door()).lock
        self.manor.cell(cur_pos).doors[d] = Door(_lock=lock_level, _leads_to=nxt_pos)

        back = d.opposite()
        self.manor.cell(nxt_pos).room = room
        self.manor.cell(nxt_pos).doors[back] = Door(_lock=LockLevel.UNLOCKED, _leads_to=cur_pos)

        # 4. Déplacement (1 step)
        if self.player.inventory.steps > 0:
            self.player.inventory.steps -= 1
        self.player.pos = nxt_pos

        # 5. Effet d'entrée + spawn d'objets
        room.on_enter(self, nxt_pos.r, nxt_pos.c)
        self.spawn_objects_for_room(nxt_pos)

        # 6. Finalisation
        self.current_draw_choices = []
        self.game_state = 'playing'
        self.current_draw_target = None

    # --- Ancienne génération aléatoire (gardée pour compat) ---
    def generate_random_room(self, r: int, c: int) -> Room:
        possible_rooms = [
            PlainRoom(), Kitchen(), Pantry(), LockerRoom(), TreasureRoom(), Garden(), Armory(), Library()
        ]
        filtered_rooms = [room for room in possible_rooms if room.can_be_placed(r, c)]
        filtered_rooms = [room for room in filtered_rooms if self.player.inventory.gems >= getattr(room, 'gem_cost', 0)]
        if not filtered_rooms:
            return PlainRoom()
        weights = [pow(1/3, getattr(room, 'rarity', 0)) for room in filtered_rooms]
        return random.choices(filtered_rooms, weights=weights, k=1)[0]

    # --- Action principale : ouvrir ou placer (2.7) ---
    def open_or_place(self, d: Direction) -> bool:
        """
        Tente d'ouvrir la porte. Si succès, passe à l'état de tirage ('drawing_room').
        """
        cur = self.player.pos
        nxt = self._neighbor(cur, d)
        if nxt is None:
            return False

        tgt_cell = self.manor.cell(nxt)
        cur_cell = self.manor.cell(cur)

        # Cas 1 : la pièce existe déjà -> rien à faire ici
        if tgt_cell.room is not None:
            return False

        # Cas 2 : nouvelle porte (on lui assigne un niveau de lock)
        if d not in cur_cell.doors:
            lock_level = self._random_lock_for_row(nxt.r)
            cur_cell.doors[d] = Door(_lock=lock_level, _leads_to=nxt)
        else:
            _ = cur_cell.doors[d].lock  # conserve l'info si besoin

        # Vérifier l'ouverture
        door = cur_cell.doors[d]
        if door.can_open(self.player.inventory):
            # consomme clé/kit si besoin
            door.open(self.player.inventory)

            # Phase de tirage
            self.current_draw_target = (cur, d)
            self.current_draw_choices = self.draw_rooms(nxt.r, nxt.c, d)

            if not self.current_draw_choices:
                self.game_state = 'lost_blocked'
                return False

            self.game_state = 'drawing_room'
            return True
        else:
            # Pas le bon outil/clé
            return False

    def move(self, d: Direction) -> bool:
        """Se déplacer via une porte déjà ouverte ; consomme 1 step."""
        cur_cell = self.manor.cell(self.player.pos)
        door = cur_cell.doors.get(d)
        if not door:
            return False
        if door.lock != LockLevel.UNLOCKED:
            return False
        if self.player.inventory.steps <= 0:
            return False

        # Déplacement
        self.player.inventory.steps -= 1
        self.player.pos = door.leads_to

        # Effet d'entrée
        new_cell = self.manor.cell(self.player.pos)
        if new_cell.room:
            new_cell.room.on_enter(self, self.player.pos.r, self.player.pos.c)
        return True

    def reached_exit(self) -> bool:
        return self.player.pos == self.manor.goal

    # --- 2.6 : génération de locks par rangée ---
    def _random_lock_for_row(self, row: int) -> LockLevel:
        row = max(0, min(self.manor.rows - 1, row))

        if row == self.manor.rows - 1:
            return LockLevel.UNLOCKED
        if row == 0:
            return LockLevel.DOUBLE_LOCKED

        if row == 3:
            p = random.random()
            if p < 0.70:
                return LockLevel.UNLOCKED
            else:
                return LockLevel.LOCKED

        if row == 2:
            p = random.random()
            if p < 0.40:
                return LockLevel.UNLOCKED
            elif p < 0.90:
                return LockLevel.LOCKED
            else:
                return LockLevel.DOUBLE_LOCKED

        if row == 1:
            p = random.random()
            if p < 0.20:
                return LockLevel.UNLOCKED
            elif p < 0.70:
                return LockLevel.LOCKED
            else:
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
