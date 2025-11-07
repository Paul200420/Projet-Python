from __future__ import annotations
from dataclasses import dataclass
import random

from enums.direction import Direction
from enums.lock_level import LockLevel
from models.coord import Coord
from models.door import Door
from world.manor import Manor
from actors.player import Player

# toutes tes rooms
from rooms.special_rooms import (
    Kitchen, Pantry, Garden, LockerRoom,
    Armory, Library, PlainRoom,
    Furnace, Greenhouse, Solarium, Veranda, MaidsChamber,
    EntranceHall, Antechamber, WeightRoom, MasterBedroom,
    UtilityRoom, ChamberOfMirrors, RumpusRoom   # 👈 
)

# objets
from objects.consumable import Apple, Banana, Cake, Sandwich, Meal
from objects.permanent import (
    ShovelObj, HammerObj, LockpickKitObj, MetalDetectorObj, RabbitFootObj
)
from objects.interactive import Chest, DigSpot, Locker
from items.permanent_item import PermanentItem


@dataclass
class Game:
    manor: Manor

    def __post_init__(self):
        # Place les rooms de base
        self.player = Player(self.manor.start)
        self.manor.cell(self.manor.start).room = EntranceHall()
        self.manor.cell(self.manor.goal).room = Antechamber()

        # ici pour le ChamberOfMirrors qui ajoute une autre salle pour les choix
        self.extra_room_classes = []

        # tirage en cours (partie 2.7)
        self.current_room_choices = []      # Liste des 3 pièces tirées
        self.current_draw_position = None   # Coord de la salle qu’on est en train de placer
        self.current_draw_direction = None  # direction depuis la salle du joueur

        # pour Veranda & co : modif temporaire des loots
        self.temporary_loot_modifiers = {}

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

    # =============================
    # GESTION DES OBJETS DE SALLE
    # =============================
    def spawn_objects_for_room(self, coord):
        # """Place automatiquement des objets dans une salle selon son type."""
        cell = self.manor.cell(coord)
        room = cell.room
        if room is None:
            return  # sécurité

        # on note combien il y avait d’objets AVANT
        before_len = len(room.contents)

        # petit filet de sécu
        if not hasattr(self, "temporary_loot_modifiers") or self.temporary_loot_modifiers is None:
            self.temporary_loot_modifiers = {}

        # petit helper local pour appliquer un boost
        def boosted_choice(candidates, name_hint=None):
            """
            candidates = [obj1, obj2, ...]
            si on a un multiplicateur sur le nom de l’objet
            (dans self.temporary_loot_modifiers), on le prend en compte.
            """
            if not self.temporary_loot_modifiers:
                return random.choice(candidates)
            weights = []
            for obj in candidates:
                obj_name = obj.__class__.__name__
                mult = self.temporary_loot_modifiers.get(obj_name, 1.0)
                weights.append(mult)
            return random.choices(candidates, weights=weights, k=1)[0]

        #  ucune apparition dans ces salles
        if isinstance(room, (EntranceHall, Antechamber)):
            return

        # =============================
        # 🧑‍🍳 SALLES DE NOURRITURE
        # =============================
        if isinstance(room, Kitchen):
            # Beaucoup de nourriture (éventuellement boostée par Veranda)
            food = [Apple(), Banana(), Cake(), Sandwich(), Meal()]
            obj = boosted_choice(food, name_hint="Food")
            room.contents.append(obj)

        elif isinstance(room, Pantry):
            # Nourriture plus forte
            strong_food = [Sandwich(), Meal()]
            obj = boosted_choice(strong_food, name_hint="FoodStrong")
            room.contents.append(obj)

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
        # 💎 SALLE TRÉSOR = UtilityRoom
        # =============================
        elif isinstance(room, UtilityRoom):
            room.contents.append(Chest())
            if random.random() < 0.5:
                perm = [ShovelObj(), HammerObj(), LockpickKitObj(), MetalDetectorObj()]
                obj = boosted_choice(perm, name_hint="Permanent")
                room.contents.append(obj)

        # =============================
        # ⚔️ ARMORY
        # =============================
        elif isinstance(room, Armory):
            perm = [ShovelObj(), HammerObj(), LockpickKitObj(), MetalDetectorObj()]
            obj = boosted_choice(perm, name_hint="Permanent")
            room.contents.append(obj)

        # =============================
        # 📚 LIBRARY
        # =============================
        elif isinstance(room, Library):
            rare = [RabbitFootObj(), ShovelObj(), MetalDetectorObj(), Apple()]
            obj = boosted_choice(rare, name_hint="LibraryLoot")
            room.contents.append(obj)

        # =============================
        # 🧱 Plain Room
        # =============================
        elif isinstance(room, PlainRoom):
            if random.random() < 0.2:
                simple = [Apple(), Banana(), ShovelObj()]
                obj = boosted_choice(simple, name_hint="PlainLoot")
                room.contents.append(obj)
        # sinon ne rien faire

        # =============================
       
        # =============================
        # condition : il existait un boost ET la salle n’a rien ajouté
         #  FALLBACK SI une salle boostée (Veranda) n’a finalement rien eu
        # 60% de chance de forcer un loot de nourriture (au lieu de 100%)
        if self.temporary_loot_modifiers and len(room.contents) == before_len:
            if random.random() < 0.50:  # 50% de chance
                fallback_food = [Apple(), Banana(), Cake(), Sandwich(), Meal()]
                try:
                    forced = boosted_choice(fallback_food)
                except NameError:
                    forced = random.choice(fallback_food)
                room.contents.append(forced)

    # =============================
    # TIRAGE DES PIÈCES (partie 2.7)
    # =============================
    def draw_three_rooms(self, r: int, c: int, direction: Direction) -> list:
        possible_rooms = [
            PlainRoom(), Kitchen(), Pantry(), LockerRoom(), UtilityRoom(),
            Garden(), Armory(), Library(), Furnace(), Greenhouse(),
            Solarium(), Veranda(), MaidsChamber(),
            WeightRoom(), MasterBedroom(), ChamberOfMirrors()
        ]

        # Pour ChamberOfMirrors, la salle Rumpus est ajoutée dynamiquement
        for cls in self.extra_room_classes:
            possible_rooms.append(cls())

        # filtrage par conditions de placement + porte dans la bonne direction
        filtered_rooms = [
            room for room in possible_rooms
            if room.can_be_placed(r, c) and direction in room.possible_doors
        ]

        if not filtered_rooms:
            return [PlainRoom()]

        # poids de base selon la rareté
        weights = [pow(1 / 3, room.rarity) for room in filtered_rooms]

        # Ajustements selon l'inventaire (ex: détecteur, patte de lapin)
        inv = self.player.inventory
        for i, room in enumerate(filtered_rooms):
            if inv.has_tool(PermanentItem.METAL_DETECTOR):
                if isinstance(room, (UtilityRoom, Armory)):
                    weights[i] *= 1.8
            if inv.has_tool(PermanentItem.RABBIT_FOOT):
                if isinstance(room, (Pantry, PlainRoom, Kitchen)):
                    weights[i] *= 1.25

        # Modificateurs contextuels (fournis par la room actuelle)
        try:
            cur_room = self.manor.cell(self.player.pos).room
        except Exception:
            cur_room = None
        if cur_room is not None:
            mods = getattr(cur_room, 'draw_modifiers', {}) or {}
            for i, room in enumerate(filtered_rooms):
                cls_name = room.__class__.__name__
                if cls_name in mods:
                    try:
                        mult = float(mods[cls_name])
                        weights[i] *= mult
                    except Exception:
                        pass

        # Sélection finale : 3 rooms distinctes,
        # avec si possible au moins une room gratuite
        selected_rooms = []
        zero_cost_found = False
        while len(selected_rooms) < 3:
            if len(selected_rooms) == 2 and not zero_cost_found:
                free_rooms = [r for r in filtered_rooms if r.gem_cost == 0]
                if free_rooms:
                    room = random.choices(
                        free_rooms,
                        weights=[pow(1 / 3, r.rarity) for r in free_rooms],
                        k=1
                    )[0]
                    selected_rooms.append(room)
                    break

            room = random.choices(filtered_rooms, weights=weights, k=1)[0]
            if room.gem_cost == 0:
                zero_cost_found = True
            if room not in selected_rooms:
                selected_rooms.append(room)

        return selected_rooms

    def retry_draw(self, r: int, c: int, direction: Direction) -> list:
        # Re-tire 3 salles si le joueur a des dés (dice > 0), et consomme 1 dé
        if self.player.inventory.dice <= 0:
            return []
        self.player.inventory.dice -= 1
        return self.draw_three_rooms(r, c, direction)

    # =============================
    # GESTION DES PORTES / SALLES
    # =============================
    def open_or_place(self, d: Direction) -> bool:
        """
        Ouvre/pose une salle adjacente dans la direction d, si possible.
        - Vérifie le coût en gemmes et les conditions de placement
        - Ne crée que les portes autorisées par la salle
        - Crée des portes bidirectionnelles UNLOCKED / ou cohérentes selon la logique de verrou
        """
        cur = self.player.pos
        nxt = self._neighbor(cur, d)
        if nxt is None:
            return False

        tgt_cell = self.manor.cell(nxt)

        # si la case est vide et qu'on n'a pas encore de choix -> on lance le tirage
        if tgt_cell.room is None and not self.current_room_choices:
            self.current_room_choices = self.draw_three_rooms(nxt.r, nxt.c, d)
            self.current_draw_position = nxt
            self.current_draw_direction = d
            return True  # on affiche les 3 choix
        elif tgt_cell.room is None and self.current_room_choices:
            # une pièce vient d’être posée → ne rien faire de plus ici
            return True

        # sinon la salle existe déjà → on ne fait que créer la porte
        cur_cell = self.manor.cell(cur)
        if d not in cur_cell.doors:
            lock_level = self._random_lock_for_row(nxt.r)
            cur_cell.doors[d] = Door(_lock=lock_level, _leads_to=nxt)

        # porte retour
        back = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }[d]
        if back not in tgt_cell.doors and back in tgt_cell.room.possible_doors:
            lock_back = cur_cell.doors[d].lock
            tgt_cell.doors[back] = Door(_lock=lock_back, _leads_to=cur)

        return True

    # =============================
    # DÉPLACEMENT / INTERACTIONS
    # =============================
    def move(self, d: Direction) -> bool:
        # Se déplacer via une porte ouverte; consomme 1 step.
        cur_cell = self.manor.cell(self.player.pos)
        door = cur_cell.doors.get(d)
        cur = self.player.pos

        if not door:
            return False
        if not door.can_open(self.player.inventory):
            return False
        if not door.open(self.player.inventory):
            return False

        # Une fois traversée, la porte est considérée ouverte définitivement dans les deux sens
        self._unlock_both_sides(cur, d)

        # Consomme 1 pas
        if self.player.inventory.steps <= 0:
            return False
        self.player.inventory.steps -= 1

        # Déplacement
        self.player.pos = door.leads_to

        # Effet de salle à l'entrée
        new_cell = self.manor.cell(self.player.pos)
        if new_cell.room:
            new_cell.room.on_enter(self, self.player.pos.r, self.player.pos.c)

        return True

    def reached_exit(self) -> bool:
        return self.player.pos == self.manor.goal

    # =============================
    # OBJETS
    # =============================
    def place_object_at(self, coord, obj) -> bool:
        # Place un objet dans la room à coord. Retourne False si pas de room.
        if not self.manor.in_bounds(coord):
            return False
        cell = self.manor.cell(coord)
        if cell.room is None:
            return False
        cell.room.contents.append(obj)
        return True

    def pick_up_here(self) -> str | None:
        # Interagit avec le premier objet de la room du joueur; retire s'il est consommé.
        cell = self.manor.cell(self.player.pos)
        if not cell.room or not cell.room.contents:
            return None
        obj = cell.room.contents[0]
        msg = obj.on_interact(self)
        if getattr(obj, "consumed", False):
            cell.room.contents.pop(0)
        return msg

    # =============================
    # VERROUILLAGE (2.8)
    # =============================
    def _random_lock_for_row(self, row: int) -> LockLevel:
        # Tire aléatoirement le niveau de verrouillage d'une porte en fonction
        # de la rangée (0 = haut / 8 = bas).
        row = max(0, min(self.manor.rows - 1, row))  # sécurité

        # Règles extrêmes fixes
        if row == self.manor.rows - 1:  # rangée 8 (bas / départ)
            return LockLevel.UNLOCKED
        if row == 0:  # rangée 0 (haut / antichambre)
            return LockLevel.DOUBLE_LOCKED

        p = random.random()

        if row == 7:
            return LockLevel.UNLOCKED if p < 0.80 else LockLevel.LOCKED
        elif row == 6:
            if p < 0.65:
                return LockLevel.UNLOCKED
            elif p < 0.95:
                return LockLevel.LOCKED
            else:
                return LockLevel.DOUBLE_LOCKED
        elif row == 5:
            if p < 0.50:
                return LockLevel.UNLOCKED
            elif p < 0.90:
                return LockLevel.LOCKED
            else:
                return LockLevel.DOUBLE_LOCKED
        elif row == 4:
            if p < 0.35:
                return LockLevel.UNLOCKED
            elif p < 0.80:
                return LockLevel.LOCKED
            else:
                return LockLevel.DOUBLE_LOCKED
        elif row == 3:
            if p < 0.25:
                return LockLevel.UNLOCKED
            elif p < 0.70:
                return LockLevel.LOCKED
            else:
                return LockLevel.DOUBLE_LOCKED
        elif row == 2:
            if p < 0.15:
                return LockLevel.UNLOCKED
            elif p < 0.60:
                return LockLevel.LOCKED
            else:
                return LockLevel.DOUBLE_LOCKED
        elif row == 1:
            if p < 0.05:
                return LockLevel.UNLOCKED
            elif p < 0.40:
                return LockLevel.LOCKED
            else:
                return LockLevel.DOUBLE_LOCKED

        return LockLevel.UNLOCKED

    def _unlock_both_sides(self, from_coord: Coord, d: Direction) -> None:
        # """Met la porte traversée ET sa porte jumelle en UNLOCKED."""
        cur_cell = self.manor.cell(from_coord)
        door = cur_cell.doors.get(d)
        if not door:
            return

        # Déverrouille la porte traversée
        door.lock = LockLevel.UNLOCKED

        # Déverrouille la porte jumelle (sens inverse) si elle existe
        back = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }[d]
        tgt_cell = self.manor.cell(door.leads_to)
        twin = tgt_cell.doors.get(back)
        if twin:
            twin.lock = LockLevel.UNLOCKED

    # =============================
    # PARTIE 2.7 / 2.8
    # =============================
    def get_current_room_choices(self) -> list:
        return self.current_room_choices

    def choose_room(self, index: int) -> bool:
        if not self.current_room_choices or not 0 <= index < len(self.current_room_choices):
            return False

        chosen_room = self.current_room_choices[index]
        tgt_cell = self.manor.cell(self.current_draw_position)

        # Cohérence : la pièce choisie doit autoriser une porte dans la direction du tirage
        if self.current_draw_direction not in chosen_room.possible_doors:
            return False
        # Vérifier le coût en gemmes
        if self.player.inventory.gems < chosen_room.gem_cost:
            return False

        # Déduction du coût et pose
        self.player.inventory.gems -= chosen_room.gem_cost
        tgt_cell.room = chosen_room
        self.spawn_objects_for_room(self.current_draw_position)

        # Réinitialisation complète après le choix
        self.current_room_choices = []
        self.current_draw_position = None
        self.current_draw_direction = None
        return True

    def redraw_rooms(self) -> bool:
        # Re-tire une nouvelle série de 3 salles pour la même position/direction, en consommant 1 dé
        if not self.current_draw_position or not self.current_draw_direction:
            return False

        new_choices = self.retry_draw(
            self.current_draw_position.r,
            self.current_draw_position.c,
            self.current_draw_direction
        )

        if not new_choices:
            return False

        self.current_room_choices = new_choices
        return True
    
    