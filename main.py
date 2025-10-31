import pygame
from world.manor import Manor
from game.game import Game
from renderer import Renderer
from enums.direction import Direction
from items.permanent_item import PermanentItem

def main():
    pygame.init()

    manor = Manor()
    game = Game(manor)

    # Optionnel : donner un outil permanent de test
    game.player.inventory.add_tool(PermanentItem.LOCKPICK_KIT)

    renderer = Renderer(game)

    running = True
    while running:
        renderer.clock.tick(25)  # limite FPS ~25

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ---- CLAVIER ----
            if event.type == pygame.KEYDOWN:

                # Quitter avec ESC
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Déplacement joueur
                if event.key == pygame.K_UP:
                    renderer.current_dir = Direction.UP
                    if game.open_or_place(Direction.UP):
                        msg = game.move(Direction.UP)
                        renderer.show_message(str(msg))

                if event.key == pygame.K_DOWN:
                    renderer.current_dir = Direction.DOWN
                    if game.open_or_place(Direction.DOWN):
                        msg = game.move(Direction.DOWN)
                        renderer.show_message(str(msg))

                if event.key == pygame.K_LEFT:
                    renderer.current_dir = Direction.LEFT
                    if game.open_or_place(Direction.LEFT):
                        msg = game.move(Direction.LEFT)
                        renderer.show_message(str(msg))

                if event.key == pygame.K_RIGHT:
                    renderer.current_dir = Direction.RIGHT
                    if game.open_or_place(Direction.RIGHT):
                        msg = game.move(Direction.RIGHT)
                        renderer.show_message(str(msg))

                # ---- INTERACTION OBJET : F ----
                if event.key == pygame.K_f:
                    result = game.interact_with_current_object()
                    renderer.show_message(result)

        renderer.draw()

    pygame.quit()


if __name__ == "__main__":
    main()
