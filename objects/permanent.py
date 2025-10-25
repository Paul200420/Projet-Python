from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from objects.base import GameObject
from items.permanent_item import PermanentItem

@dataclass
class Permanent(GameObject):
    """Objet permanent : une fois ramassé, il va dans Inventory.tools."""
    _tool: PermanentItem = PermanentItem.SHOVEL  # valeur par défaut; chaque sous-classe la surchargera

    @property
    def tool(self) -> PermanentItem:
        return self._tool

    @tool.setter
    def tool(self, value: PermanentItem) -> None:
        self._tool = value

    def on_interact(self, game: "Game") -> str:
        if self.consumed:
            return f"{self.name} déjà ramassé."
        inv = game.player.inventory
        if self._tool in inv.tools:
            self.consumed = True
            return f"{self.name} (déjà possédé)."
        inv.add_tool(self._tool)
        self.consumed = True
        return f"{self.name} ajouté aux outils."

# ---- Sous-classes concrètes (pratique pour placer par type + image dédiée) ----

class ShovelObj(Permanent):
    def __init__(self, image_path: Optional[str] = "assets/rooms/items/shovel.png"):
        super().__init__(_name="Shovel", _image_path=image_path, _tool=PermanentItem.SHOVEL)

class HammerObj(Permanent):
    def __init__(self, image_path: Optional[str] = "assets/rooms/items/hammer.png"):
        super().__init__(_name="Hammer", _image_path=image_path, _tool=PermanentItem.HAMMER)

class LockpickKitObj(Permanent):
    def __init__(self, image_path: Optional[str] = "assets/rooms/items/lockpick.png"):
        super().__init__(_name="Lockpick Kit", _image_path=image_path, _tool=PermanentItem.LOCKPICK_KIT)

class MetalDetectorObj(Permanent):
    def __init__(self, image_path: Optional[str] = "assets/rooms/items/metal_detector.png"):
        super().__init__(_name="Metal Detector", _image_path=image_path, _tool=PermanentItem.METAL_DETECTOR)

class RabbitFootObj(Permanent):
    def __init__(self, image_path: Optional[str] = "assets/rooms/items/rabbit_foot.png"):
        super().__init__(_name="Rabbit Foot", _image_path=image_path, _tool=PermanentItem.RABBIT_FOOT)
