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
            # Niveau de verrouillage basé sur la rangée de la salle cible
            lock_level = self._random_lock_for_row(nxt.r)#On tire un niveau de verrou pour la porte aller en fonction de la rangée de la salle cible (plus on monte, plus c’est verrouillé).
            cur_cell.doors[d] = Door(_lock=lock_level, _leads_to=nxt)

        # Crée la porte retour si autorisée
        back = {Direction.UP: Direction.DOWN, Direction.DOWN: Direction.UP,
                Direction.LEFT: Direction.RIGHT, Direction.RIGHT: Direction.LEFT}[d]
        
        if back not in tgt_cell.doors and back in tgt_cell.room.possible_doors:
            #cohérence : on met le même niveau de verrou sur la porte retour
            lock_level_back = cur_cell.doors[d].lock
            tgt_cell.doors[back] = Door(_lock=lock_level_back, _leads_to=cur)

        return True

    def move(self, d: Direction) -> bool:
        """Se déplacer via une porte ouverte; consomme 1 step."""
        cur_cell = self.manor.cell(self.player.pos)
        door = cur_cell.doors.get(d)
        cur = self.player.pos
        
        if not door:
            return False
        if not door.can_open(self.player.inventory):
            return False
        if not door.open(self.player.inventory):
            return False
        #2.6 modif
         #Une fois traversée, la porte est considérée ouverte définitivement dans les deux sens
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

    ######.    2.6
    def _random_lock_for_row(self, row: int) -> LockLevel:
    #Logique proposé :
    #Tire aléatoirement le niveau de verrouillage d'une porte en fonction de la rangée (0 en haut → 4 en bas).
    #Rangée 4 (départ) : toujours UNLOCKED
    #Rangée 0 (antichambre) : toujours DOUBLE_LOCKED
    #Intermédiaires : proba croissantes de LOCKED / DOUBLE_LOCKED en remontant
    
    # Sécurité : bornes
        row = max(0, min(self.manor.rows - 1, row))

        if row == self.manor.rows - 1:  # rangée 4 (bas, départ)
            return LockLevel.UNLOCKED
        if row == 0:                    # rangée 0 (haut, antichambre)
            return LockLevel.DOUBLE_LOCKED

    # Probabilités intermédiaires (r=3,2,1)
    # Tu peux ajuster ces chiffres si tu veux un jeu plus dur/facile.
    # r=3 (juste au-dessus du départ)
        if row == 3:
            p = random.random()
            if p < 0.70: return LockLevel.UNLOCKED
            else:        
                return LockLevel.LOCKED

    # r=2 (milieu)
        if row == 2:
            p = random.random()
            if p < 0.40: 
                return LockLevel.UNLOCKED
            elif p < 0.90: 
                return LockLevel.LOCKED
            else:          
                return LockLevel.DOUBLE_LOCKED

    # r=1 (avant-dernier étage)
        if row == 1:
            p = random.random()
            if p < 0.20: 
                return LockLevel.UNLOCKED
            elif p < 0.70: 
                return LockLevel.LOCKED
            else:          
                return LockLevel.DOUBLE_LOCKED

    # fallback (ne devrait pas arriver)
        return LockLevel.UNLOCKED
    def _unlock_both_sides(self, from_coord: Coord, d: Direction) -> None:
    #"""Met la porte traversée ET sa porte jumelle en UNLOCKED."""
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
            
    #########.       2.6 
