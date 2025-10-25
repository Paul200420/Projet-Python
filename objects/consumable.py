from __future__ import annotations
from dataclasses import dataclass
from objects.base import GameObject

@dataclass
class Consumable(GameObject):
    """Objet qui augmente directement les pas du joueur quand il est ramassé."""
    _steps_gain: int = 0

    @property
    def steps_gain(self) -> int:
        return self._steps_gain

    @steps_gain.setter
    def steps_gain(self, value: int) -> None:
        self._steps_gain = value

    def on_interact(self, game: "Game") -> str:
        if self.consumed:
            return f"{self.name} déjà utilisé."
        game.player.inventory.steps += self._steps_gain
        self.consumed = True
        return f"{self.name} consommé (+{self._steps_gain} pas)"



class Apple(Consumable):
    def __init__(self, image_path: str = "assets/rooms/items/apple.png"):
        super().__init__(_name="Apple", _image_path=image_path, _steps_gain=2)

class Banana(Consumable):
    def __init__(self, image_path: str = "assets/rooms/items/banana.png"):
        super().__init__(_name="Banana", _image_path=image_path, _steps_gain=3)

class Cake(Consumable):
    def __init__(self, image_path: str = "assets/rooms/items/cake.png"):
        super().__init__(_name="Cake", _image_path=image_path, _steps_gain=10)

class Sandwich(Consumable):
    def __init__(self, image_path: str = "assets/rooms/items/sandwich.png"):
        super().__init__(_name="Sandwich", _image_path=image_path, _steps_gain=15)

class Meal(Consumable):
    def __init__(self, image_path: str = "assets/rooms/items/meal.png"):
        super().__init__(_name="Meal", _image_path=image_path, _steps_gain=25)
