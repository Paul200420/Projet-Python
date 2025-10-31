from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Set 
from enums.direction import Direction
from enums.lock_level import LockLevel
from models.coord import Coord
from models.door import Door
from world.manor import Manor
from actors.player import Player
import random

# Imports pour les nouveaux modèles et types
from models.room_deck_item import RoomDeckItem # [NOUVEAU] Doit être créé dans models/
from models.room import Room 
from enums.room_colors import CouleurPiece 

from rooms.room_base import Room
from rooms.special_room import (
    Kitchen, Pantry, Garden, LockerRoom,
    TreasureRoom, Armory, Library, PlainRoom,
    EntranceHall, Antechamber
)
from objects.consumable import Apple, Banana, Cake, Sandwich, Meal
from objects.permanent import ShovelObj, HammerObj, LockpickKitObj, MetalDetectorObj, RabbitFootObj
from objects.interactive import Chest, DigSpot, Locker

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

    # --- NOUVEAUX ATTRIBUTS D'ÉTAT (Section 2.7) ---
    room_deck: List[RoomDeckItem] = field(default_factory=list) 
    game_state: str = 'playing'        
    current_draw_choices: List[Room] = field(default_factory=list) 
    current_draw_target: tuple[Coord, Direction] = None   

    def __post_init__(self):
        self.player = Player(self.manor.start)
        
        # Initialisation de la pioche 
        self.room_deck = self._initialize_room_deck() 

        # Place les rooms de base et les retire de la pioche
        self.manor.cell(self.manor.start).room = self._get_and_remove_room("EntranceHall")
        self.manor.cell(self.manor.goal).room = self._get_and_remove_room("Antechamber")
        
    def _initialize_room_deck(self) -> List[RoomDeckItem]:
        """Crée la pioche complète en encapsulant chaque Room."""
        all_room_definitions = self._get_all_room_definitions() 
        return [RoomDeckItem(room=r) for r in all_room_definitions]

    def _get_and_remove_room(self, name: str) -> Room:
        """Récupère une Room du deck par nom et la marque comme non disponible."""
        for item in self.room_deck:
            if item.room.name == name and item.is_in_deck:
                item.is_in_deck = False
                return item.room
        return PlainRoom(_name=name)
        
    def _get_all_room_definitions(self) -> List[Room]:
        """LISTE COMPLÈTE DE TOUTES LES PIÈCES DANS LE JEU (Y COMPRIS DOUBLONS)."""
        # Ceci est une liste d'exemple : VOUS DEVEZ LA COMPLÉTER AVEC VOS INSTANCES DE ROOM
        return [
            EntranceHall(_name="EntranceHall", _possible_doors={Direction.UP}),
            Antechamber(_name="Antechamber", _possible_doors={Direction.DOWN}),
            PlainRoom(_name="PlainRoom"), PlainRoom(_name="PlainRoom"), PlainRoom(_name="PlainRoom"), 
            Kitchen(_name="Kitchen"), Pantry(_name="Pantry"), LockerRoom(_name="LockerRoom"),
            TreasureRoom(_name="TreasureRoom", _rarity=2, _gem_cost=1),
            # ... toutes les autres classes de Room que vous avez...
        ]

    # --- outils internes ---
    def _neighbor(self, coord, direction):
        dr, dc = Direction.delta(direction)
        nxt = Coord(coord.r + dr, coord.c + dc)
        if not self.manor.in_bounds(nxt):
            return None
        return nxt
        
    # --- LOGIQUE D'ALÉATOIRE D'OBJETS ET BUTIN (Section 2.8) ---
    def open_container_content(self, container_type: str) -> List['GameObject']:
        """Tire aléatoirement les objets obtenus d'un conteneur (coffre, trou à creuser)."""
        if container_type not in LOOT_TABLES: return []

        loot_table = LOOT_TABLES[container_type]
        loot_choices = list(loot_table.keys())
        loot_weights = list(loot_table.values())

        selected_type = random.choices(loot_choices, weights=loot_weights, k=1)[0]
        
        # NOTE: Vous devez avoir une méthode self.create_game_object() qui crée l'objet réel
        if selected_type == "Gold":
            return [self.create_game_object("Gold", random.randint(10, 30))]
        elif selected_type == "Key":
            return [self.create_game_object("Key")]
        elif selected_type == "Food_Steps":
            return [self.create_game_object(random.choice(["Apple", "Banana", "Cake"]))]
        elif selected_type == "PermanentItem_Random":
            return [self.create_game_object(random.choice(["ShovelObj", "HammerObj", "LockpickKitObj"]))]
        
        return []

    # --- MÉTHODE EXISTANTE AVEC AJOUTS 2.8 ---
    def spawn_objects_for_room(self, coord):
        cell = self.manor.cell(coord)
        room = cell.room
        if room is None: return

        if isinstance(room, (EntranceHall, Antechamber)): return

        # Logique existante pour les salles spécifiques
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
        
        # --- NOUVEAU: Aléatoire et effets permanents (Patte de Lapin, Détecteur) ---
        
        # Chance de Coffre (Patte de lapin)
        base_chest_chance = 0.20
        if self.player.inventory.has_rabbit_foot:
            base_chest_chance *= 1.3 

        if random.random() < base_chest_chance:
            room.contents.append(Chest())
            
        # Chance de Clé/Or (Détecteur de métaux)
        base_key_chance = 0.05
        if self.player.inventory.has_metal_detector:
            base_key_chance *= 2.0 
        
        if random.random() < base_key_chance:
            room.contents.append(self.create_game_object("Key")) 
            
        # Logique Plain Room existante
        elif isinstance(room, PlainRoom):
            if random.random() < 0.2:
                room.contents.append(random.choice([Apple(), Banana(), ShovelObj()]))

    # --- LOGIQUE DE TIRAGE ET RARETÉ (Section 2.7) ---

    def _get_draw_modifier(self, room: Room) -> float:
        """Calcule le modificateur de probabilité de tirage basé sur les effets actifs."""
        modifier = 1.0
        current_room = self.manor.cell(self.player.pos).room
        
        if current_room and current_room.name == "Greenhouse" and room.couleur == CouleurPiece.VERTE:
            modifier *= 2.0
            
        return modifier

    def draw_rooms(self, target_r: int, target_c: int, direction_from_cur: Direction) -> List[Room]:
        """Tire trois pièces de la pioche en respectant les règles (Section 2.7)."""
        possible_items = []
        back_direction = direction_from_cur.opposite()
        
        for item in self.room_deck:
            room = item.room
            
            if not item.is_in_deck: continue
            
            if room.can_be_placed(target_r, target_c) and back_direction in room.possible_doors:
                modifier = self._get_draw_modifier(room)
                possible_items.append({'item': item, 'modifier': modifier})

        if len(possible_items) == 0: return []

        # Pondération : (1 / (3 ** rarity)) * modifier
        items_list = [item['item'] for item in possible_items]
        weights = [(1 / (3 ** item['item'].room.rarity)) * item['modifier'] for item in possible_items]
        k = min(3, len(items_list))
        
        choices = random.choices(items_list, weights=weights, k=k)
        choices_rooms = [item.room for item in choices]

        # Garantie de la Pièce Gratuite (Section 2.7)
        if not any(room.gem_cost == 0 for room in choices_rooms):
            free_items_in_deck = [item for item in self.room_deck 
                                  if item.is_in_deck and item.room.gem_cost == 0 and item not in choices]
            if free_items_in_deck:
                item_to_replace = max(choices, key=lambda item: item.room.gem_cost + item.room.rarity * 5)
                choices.remove(item_to_replace)
                choices.append(random.choice(free_items_in_deck))

        self.current_draw_choices = [item.room for item in choices]
        return self.current_draw_choices

    def reroll_draw_choices(self):
        """Dépense un dé pour retirer trois pièces dans la pioche (Section 2.7)."""
        if self.player.inventory.dice >= 1:
            self.player.inventory.dice -= 1
            cur_pos, d = self.current_draw_target
            nxt_pos = self._neighbor(cur_pos, d) 
            self.current_draw_choices = self.draw_rooms(nxt_pos.r, nxt_pos.c, d)
            return True
        return False

    def select_and_place_room(self, chosen_room_index: int):
        """Gère le paiement, le placement, et le déplacement après le choix."""
        room = self.current_draw_choices[chosen_room_index]
        cur_pos, d = self.current_draw_target
        nxt_pos = self._neighbor(cur_pos, d)

        # 1. Dépense des gemmes
        self.player.inventory.gems -= room.gem_cost
        
        # 2. Marquer la pièce comme utilisée (is_in_deck = False)
        for item in self.room_deck:
            if item.room is room:
                item.is_in_deck = False
                break

        # 3. Placement et connexion des portes
        lock_level = self.manor.cell(cur_pos).doors[d].lock 
        self.manor.cell(cur_pos).doors[d] = Door(_lock=lock_level, _leads_to=nxt_pos) 
        
        back = d.opposite()
        self.manor.cell(nxt_pos).room = room
        self.manor.cell(nxt_pos).doors[back] = Door(_lock=LockLevel.UNLOCKED, _leads_to=cur_pos) 

        # 4. Déplacement du joueur (consomme 1 pas)
        self.player.pos = nxt_pos
        self.player.inventory.steps -= 1
        
        # 5. Effet de salle à l'entrée et spawn d'objets
        room.on_enter(self, nxt_pos.r, nxt_pos.c)
        self.spawn_objects_for_room(nxt_pos)

        # 6. Finalisation
        self.current_draw_choices = []
        self.game_state = 'playing'

    # --- MÉTHODE EXISTANTE (Devient obsolète mais reste pour compatibilité) ---
    def generate_random_room(self, r: int, c: int):
        # Cette méthode n'est plus utilisée dans la nouvelle logique de open_or_place
        possible_rooms = [
             PlainRoom(), Kitchen(), Pantry(), LockerRoom(), TreasureRoom(), Garden(), Armory(), Library()
        ]

        filtered_rooms = [room for room in possible_rooms if room.can_be_placed(r, c)]
        filtered_rooms = [room for room in filtered_rooms if self.player.inventory.gems >= room.gem_cost]

        if not filtered_rooms: return PlainRoom()

        weights = [pow(1/3, room.rarity) for room in filtered_rooms]
        return random.choices(filtered_rooms, weights=weights, k=1)[0]
    
    # --- ACTIONS DE BASE (MODIFICATION MAJEURE) ---
    def open_or_place(self, d: Direction) -> bool: 
        """
        [MODIFIÉ SECTION 2.7] Tente d'ouvrir la porte. Si succès, passe en état de tirage (drawing_room).
        """
        cur = self.player.pos
        nxt = self._neighbor(cur, d)
        if nxt is None: return False

        tgt_cell = self.manor.cell(nxt)
        cur_cell = self.manor.cell(cur)

        # Cas 1: La pièce existe déjà -> On ne fait rien 
        if tgt_cell.room is not None:
            return False 

        # Cas 2: Nouvelle porte à ouvrir (déclenchement du tirage)

        # Déterminer le niveau de verrouillage (Section 2.8)
        if d not in cur_cell.doors:
            lock_level = self._random_lock_for_row(nxt.r) 
            cur_cell.doors[d] = Door(_lock=lock_level, _leads_to=nxt) 
        else:
            lock_level = cur_cell.doors[d].lock

        # Vérification de l'ouverture
        door = cur_cell.doors[d]
        if door.can_open(self.player.inventory):
            # La porte est ouverte (dépense clé/kit si nécessaire)
            door.open(self.player.inventory)

            # Entrer en phase de tirage (Section 2.7)
            self.current_draw_target = (cur, d)
            self.current_draw_choices = self.draw_rooms(nxt.r, nxt.c, d)
            
            if not self.current_draw_choices:
                self.game_state = 'lost_blocked'
                return False

            self.game_state = 'drawing_room'
            return True
        else:
            # Échec de l'ouverture (clé/kit manquant)
            return False

    def move(self, d: Direction) -> bool: 
        """Se déplacer via une porte ouverte; consomme 1 step."""
        cur_cell = self.manor.cell(self.player.pos)
        door = cur_cell.doors.get(d)
        cur = self.player.pos
        
        if not door: return False
        
        # Le move() ne peut se faire que si la porte est déjà UNLOCKED 
        if door.lock != LockLevel.UNLOCKED: return False 

        if self.player.inventory.steps <= 0: return False
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
        
    # --- helpers objets (Non modifiés) ---
    def place_object_at(self, coord, obj) -> bool:
        """Place un objet dans la room à coord. Retourne False si pas de room."""
        if not self.manor.in_bounds(coord): return False
        cell = self.manor.cell(coord)
        if cell.room is None: return False
        cell.room.contents.append(obj)
        return True

    def pick_up_here(self) -> str | None:
        """Interagit avec le premier objet de la room du joueur; retire s'il est consommé."""
        cell = self.manor.cell(self.player.pos)
        if not cell.room or not cell.room.contents: return None
        obj = cell.room.contents[0]
        msg = obj.on_interact(self)
        if getattr(obj, "consumed", False):
            cell.room.contents.pop(0)
        return msg

    ######.     2.6 (Méthode de verrouillage existante)
    def _random_lock_for_row(self, row: int) -> LockLevel:
        row = max(0, min(self.manor.rows - 1, row))

        if row == self.manor.rows - 1:
            return LockLevel.UNLOCKED
        if row == 0:
            return LockLevel.DOUBLE_LOCKED

        if row == 3:
            p = random.random()
            if p < 0.70: return LockLevel.UNLOCKED
            else: return LockLevel.LOCKED

        if row == 2:
            p = random.random()
            if p < 0.40: return LockLevel.UNLOCKED
            elif p < 0.90: return LockLevel.LOCKED
            else: return LockLevel.DOUBLE_LOCKED

        if row == 1:
            p = random.random()
            if p < 0.20: return LockLevel.UNLOCKED
            elif p < 0.70: return LockLevel.LOCKED
            else: return LockLevel.DOUBLE_LOCKED

        return LockLevel.UNLOCKED
        
    def _unlock_both_sides(self, from_coord: Coord, d: Direction) -> None:
        """Met la porte traversée ET sa porte jumelle en UNLOCKED."""
        cur_cell = self.manor.cell(from_coord)
        door = cur_cell.doors.get(d)
        if not door: return
        
        door.lock = LockLevel.UNLOCKED

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
