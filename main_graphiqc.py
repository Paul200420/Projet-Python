import pygame, sys
from world.manor import Manor
from game.game import Game
from enums.direction import Direction
from items.permanent_item import PermanentItem
from ui.renderer import Renderer

from objects.permanent import ShovelObj, MetalDetectorObj
from objects.consumable import Apple, Cake
from objects.interactive import Chest


def run():
    manor = Manor()
    game = Game(manor)
    # juste pour ressembler au screenshot
    # game.player.inventory.add_tool(PermanentItem.SHOVEL)
    # game.player.inventory.add_tool(PermanentItem.METAL_DETECTOR)

    # Placer des objets permanents dans des rooms spécifiques
    game.place_object_at(game.player.pos, ShovelObj())
    game.place_object_at(game.player.pos, MetalDetectorObj())
    game.place_object_at(game.player.pos, Chest())


    # placer une pomme et un gâteau dans la salle de départ
    game.place_object_at(game.player.pos, Apple())
    game.place_object_at(game.player.pos, Cake())


    renderer = Renderer(game, window_width=1250, window_height=750, sidebar_ratio=0.45)


    current_dir = Direction.UP

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit(0)
                if event.key == pygame.K_UP: current_dir = Direction.UP
                if event.key == pygame.K_DOWN: current_dir = Direction.DOWN
                if event.key == pygame.K_LEFT: current_dir = Direction.LEFT
                if event.key == pygame.K_RIGHT: current_dir = Direction.RIGHT
                if event.key == pygame.K_SPACE: game.open_or_place(current_dir)
                # if event.key == pygame.K_RETURN: game.move(current_dir)
                if event.key == pygame.K_RETURN:
                    success = game.move(current_dir)
                    if not success:
                        # Déterminer pourquoi ça a échoué
                        cell = game.manor.cell(game.player.pos)
                        nxt = game._neighbor(game.player.pos, current_dir)

                        if nxt is None:
                            print("DEBUG message:", renderer.error_message)
                            renderer.error_message = f"Impossible d'aller vers {current_dir.name.title()} (hors du manoir)"
                        elif current_dir not in cell.doors:
                            renderer.error_message = f"Aucune porte dans cette direction. Appuyez sur ESPACE pour en placer une"
                        else:
                            renderer.error_message = f"Impossible d'ouvrir la porte (clé ou condition manquante)"
                    else:
                        renderer.error_message = ""  # reset si mouvement réussi
                if event.key == pygame.K_f:
                    msg = game.pick_up_here()
                    if msg:
                        renderer.error_message = msg


        renderer.current_dir = current_dir
        renderer.draw()
        renderer.clock.tick(60)

if __name__ == "__main__":
    run()
