from world.manor import Manor
from game.game import Game
from enums.direction import Direction
from items.permanent_item import PermanentItem

def main():
    """Lance une version console de démonstration : exploration automatique vers le haut avec un kit de crochetage."""
    manor = Manor()
    game = Game(manor)

    # Démo : on ajoute un kit de crochetage au joueur (montre l’usage des permanents)
    game.player.inventory.add_tool(PermanentItem.LOCKPICK_KIT)

    print("Start:", game.player.pos, "steps:", game.player.inventory.steps)

    # Explore vers le haut: ouvre/pose puis move
    if game.open_or_place(Direction.UP):
        moved = game.move(Direction.UP)
        print("Move UP:", moved, "pos:", game.player.pos, "steps:", game.player.inventory.steps)

    # On continue à monter jusqu'à la ligne de l'exit
    while game.player.pos.r > game.manor.goal.r and game.player.inventory.steps > 0:
        game.open_or_place(Direction.UP)
        game.move(Direction.UP)

    print("Reached exit?", game.reached_exit(), "pos:", game.player.pos, "steps:", game.player.inventory.steps)

if __name__ == "__main__":
    main()
