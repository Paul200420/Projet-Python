from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List
import random

from objects.base import GameObject
from objects.consumable import Apple, Banana, Cake, Sandwich, Meal
from objects.permanent import ShovelObj, HammerObj, LockpickKitObj, MetalDetectorObj, RabbitFootObj
from items.permanent_item import PermanentItem


@dataclass
class InteractiveObject(GameObject):
    """
    Classe de base pour les objets interactifs (coffres, spots, casiers).
    """
    _required_tools: List[PermanentItem] = field(default_factory=list)   # outils permanents nécessaires comme le hammer
    _can_use_key: bool = False                                           # est-ce qu'une clé peut être utilisée
    _loot_table: List[GameObject] = field(default_factory=list)          # objets possibles
    _can_be_empty: bool = False                                          # l'objet peut-il être vide ?

    @property
    def required_tools(self) -> List[PermanentItem]:
        """Retourne la liste des outils permanents nécessaires pour ouvrir cet objet."""
        return self._required_tools

    @required_tools.setter
    def required_tools(self, value: List[PermanentItem]) -> None:
        """Définit la liste des outils permanents nécessaires pour ouvrir cet objet."""
        self._required_tools = value

    @property
    def can_use_key(self) -> bool:
        """Indique si une clé peut être utilisée pour ouvrir cet objet."""
        return self._can_use_key

    @can_use_key.setter
    def can_use_key(self, value: bool) -> None:
        """Active ou désactive l'utilisation d'une clé pour ouvrir cet objet."""
        self._can_use_key = value

    @property
    def loot_table(self) -> List[GameObject]:
        """Retourne la table de butin utilisée pour générer le contenu de l'objet."""
        return self._loot_table

    @loot_table.setter
    def loot_table(self, value: List[GameObject]) -> None:
        """Définit la table de butin possible pour cet objet."""
        self._loot_table = value

    @property
    def can_be_empty(self) -> bool:
        """Indique si cet objet peut éventuellement être vide."""
        return self._can_be_empty

    @can_be_empty.setter
    def can_be_empty(self, value: bool) -> None:
        """Permet de préciser si l'objet peut être vide ou non."""
        self._can_be_empty = value

    def can_interact(self, game: "Game") -> bool:
        """Vérifie si le joueur peut interagir avec cet objet."""
        inv = game.player.inventory
        has_required_tool = any(tool in inv.tools for tool in self._required_tools)
        has_key = inv.keys > 0 if self._can_use_key else False
        return has_required_tool or has_key or len(self._required_tools) == 0

    def generate_loot(self, game: "Game") -> Optional[GameObject]:
        """Détermine ce que le joueur trouve dans l'objet.

        On supporte deux formats pour _loot_table:
        - liste d'objets -> choix uniforme
        - liste de (objet, weight) -> choix pondéré

        Certaines tools (ex: METAL_DETECTOR, RABBIT_FOOT) modifient les probabilités.
        """
        inv = game.player.inventory

        # Probabilité d'être vide (si possible) - modifiable par chance permanente
        empty_chance = 0.30
        if inv.has_tool(PermanentItem.RABBIT_FOOT):
            # Patte de lapin réduit la probabilité d'être vide
            empty_chance = max(0.05, empty_chance - 0.15)

        if self._can_be_empty and random.random() < empty_chance:
            return None

        if not self._loot_table:
            return None

        # Construire listes d'items et poids
        items = []
        weights = []
        for entry in self._loot_table:
            if isinstance(entry, tuple) and len(entry) == 2:
                item, w = entry
                items.append(item)
                weights.append(max(0.0, float(w)))
            else:
                items.append(entry)
                weights.append(1.0)

        # Modifier poids selon outils du joueur
        if inv.has_tool(PermanentItem.METAL_DETECTOR):
            # Favorise objets permanents (outils) et gemmes (approx via names)
            for i, itm in enumerate(items):
                if getattr(itm, 'tool', None) is not None:
                    weights[i] *= 2.0
                # boost items whose name contains 'Gem' or 'Treasure'
                if 'gem' in itm.name.lower() or 'treasure' in itm.name.lower():
                    weights[i] *= 1.5

        # Choix pondéré
        total = sum(weights)
        if total <= 0:
            return None
        # Normaliser et choisir
        probs = [w/total for w in weights]
        idx = random.choices(range(len(items)), weights=probs, k=1)[0]
        return items[idx]

    def on_interact(self, game: "Game") -> str:
        """Tente d'ouvrir l'objet, génère le loot si possible et le place dans la salle."""
        if self.consumed:
            return f"{self.name} est déjà vide."

        inv = game.player.inventory

        # Vérifier les conditions d'ouverture
        has_tool = any(tool in inv.tools for tool in self._required_tools)
        has_key = inv.keys > 0 if self._can_use_key else False

        if not has_tool and not has_key:
            tools_needed = [t.name for t in self._required_tools]
            return f"Vous avez besoin de {tools_needed} ou d'une clé pour ouvrir {self.name}."

        # Consommer une clé si utilisée (et si pas de marteau)
        if has_key and not has_tool:
            inv.keys = inv.keys - 1
        loot = self.generate_loot(game)
        self.consumed = True

        if loot is None:
            return f"{self.name} est vide..."

        # Déposer le loot dans la room
        game.manor.cell(game.player.pos).room.contents.append(loot)
        return f"Vous avez trouvé {loot.name} dans {self.name}!"


# ================================
# Objets interactifs concrets
# ================================

class Chest(InteractiveObject):
    """Coffre : s'ouvre avec une clé ou un marteau et contient des objets."""
    def __init__(self, image_path: str = "assets/rooms/items/chest.png"):
        super().__init__(
            _name="Chest",
            _image_path=image_path,
            _required_tools=[PermanentItem.HAMMER],  # marteau autorisé
            _can_use_key=True,                      # clé autorisée
            _loot_table=[Apple(), Banana(), Cake(), Sandwich(), Meal(), ShovelObj(), HammerObj()],
            _can_be_empty=False
        )


class DigSpot(InteractiveObject):
    """Endroit à creuser : nécessite la pelle, peut être vide ou donner des objets."""
    def __init__(self, image_path: str = "assets/rooms/items/dig_spot.png"):
        super().__init__(
            _name="Dig Spot",
            _image_path=image_path,
            _required_tools=[PermanentItem.SHOVEL],
            _can_use_key=False,
            _loot_table=[Apple(), Banana(), Sandwich()],
            _can_be_empty=True
        )


class Locker(InteractiveObject):
    """Casier : ne s'ouvre qu'avec une clé."""
    def __init__(self, image_path: str = "assets/rooms/items/locker.png"):
        super().__init__(
            _name="Locker",
            _image_path=image_path,
            _required_tools=[],     # pas de marteau ici
            _can_use_key=True,     # uniquement clé
            _loot_table=[Apple(), Meal(), RabbitFootObj()],
            _can_be_empty=True
        )


# ================================
# Vendeur (pour la Kitchen)
# ================================
class Vendor(InteractiveObject):
    """
    Comptoir de magasin : reste dans la pièce.
    Le joueur appuie sur 1..5 pour acheter depuis main_graphiqc.
    """
    def __init__(self, image_path: str = "assets/rooms/items/vendor.png"):
        super().__init__(
            _name="Shop Counter",
            _image_path=image_path,
            _required_tools=[],
            _can_use_key=False,
            _loot_table=[],
            _can_be_empty=False,
        )
        # catalogue (indexé 1..n côté affichage)
        self.catalog = [
            ("Banane", 3,   lambda g: g.place_object_at(g.player.pos, Banana())),
            ("Pomme", 3,    lambda g: g.place_object_at(g.player.pos, Apple())),
            ("Clé", 8,      lambda g: setattr(g.player.inventory, "keys", g.player.inventory.keys + 1)),
            ("Dé", 6,       lambda g: setattr(g.player.inventory, "dice", g.player.inventory.dice + 1)),
            ("Lockpick", 10, lambda g: g.player.inventory.add_tool(PermanentItem.LOCKPICK_KIT)),
        ]

    # -------- affichage dans le panneau --------
    def get_catalog_lines(self) -> list[str]:
        """Retourne les lignes de texte décrivant les articles disponibles à l'achat."""
        lines = []
        for idx, (name, price, _give) in enumerate(self.catalog, start=1):
            lines.append(f"{idx}) {name} ({price} or)")
        return lines

    # -------- achat appelé depuis main_graphiqc --------
    def buy_item(self, game: "Game", index_1based: int) -> str:
        """Tente d'acheter l'article d'indice donné dans le catalogue et applique son effet."""
        if index_1based < 1 or index_1based > len(self.catalog):
            return "Article inexistant."

        name, price, give_fun = self.catalog[index_1based - 1]
        inv = game.player.inventory

        if inv.gold < price:
            return f"Pas assez d'or pour {name} (coût : {price})."

        # payer
        inv.gold -= price

        # donner l'objet / effet
        give_fun(game)

        # remettre le vendeur en dernier pour que F prenne l'objet acheté
        cell = game.manor.cell(game.player.pos)
        if cell.room and cell.room.contents:
            # on enlève le vendor
            cell.room.contents = [o for o in cell.room.contents if o is not self]
            # on le remet à la fin
            cell.room.contents.append(self)

        return f"Achat de {name} réussi (-{price} or)."

    
    def on_interact(self, game: "Game") -> str:
        """Message générique lorsqu'on interagit avec le comptoir sans acheter."""
        return "Comptoir du magasin."
