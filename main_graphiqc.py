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

                # --- 2.5: Sélection de la direction (ZQSD + flèches) ---
                if event.key in (pygame.K_UP, pygame.K_z):
                    current_dir = Direction.UP
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    current_dir = Direction.DOWN
                if event.key in (pygame.K_LEFT, pygame.K_q):
                    current_dir = Direction.LEFT
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    current_dir = Direction.RIGHT

                # --- 2.5: ESPACE = ouvrir/placer la porte dans la direction choisie ---
                if event.key == pygame.K_SPACE:
                    nxt = game._neighbor(game.player.pos, current_dir)
                    if nxt is None:
                        renderer.error_message = "Impossible : mur (hors du manoir)."
                    else:
                        ok = game.open_or_place(current_dir)
                        renderer.error_message = "Porte ouverte." if ok else "Impossible d'ouvrir/placer la porte."

                # --- 2.5: ENTRÉE = se déplacer via porte ouverte (consomme 1 pas) ---
                if event.key == pygame.K_RETURN:
                    # Vérifs simples pour messages pédagogiques
                    if game.player.inventory.steps <= 0:
                        renderer.error_message = "Vous n'avez plus de pas."
                    else:
                        cur_cell = game.manor.cell(game.player.pos)
                        door = cur_cell.doors.get(current_dir)
                        nxt = game._neighbor(game.player.pos, current_dir)

                        if nxt is None:
                            renderer.error_message = "Impossible : mur (hors du manoir)."
                        elif door is None:
                            renderer.error_message = "Aucune porte ici. Appuyez sur ESPACE pour en placer/ouvrir une."
                        else:
                            avant = game.player.inventory.steps
                            moved = game.move(current_dir)
                            if not moved:
                                # Raison probable: verrou sans clé / ou 0 pas.
                                if avant <= 0:
                                    renderer.error_message = "Vous n'avez plus de pas."
                                else:
                                    # Porte présente mais non ouvrable (clé manquante / double verrou)
                                    if not door.can_open(game.player.inventory):
                                        renderer.error_message = "Porte verrouillée : il faut une clé (kit OK pour niveau 1)."
                                    else:
                                        renderer.error_message = "Déplacement impossible."
                            else:
                                # Succès : -1 pas déjà géré par Game.move()
                                renderer.error_message = f"Déplacement réussi (-1 pas). Pas restants : {game.player.inventory.steps}"

                                # Victoire : arrivée atteinte
                                if game.reached_exit():
                                    renderer.error_message = "🎉 Vous avez atteint l'antichambre !"
                                    renderer.draw()
                                    pygame.time.wait(1800)
                                    pygame.quit(); sys.exit(0)

                # --- Ramasser / interagir avec l'objet en tête de salle ---
                if event.key == pygame.K_f:
                    msg = game.pick_up_here()
                    if msg:
                        renderer.error_message = msg

        renderer.current_dir = current_dir
        renderer.draw()
        renderer.clock.tick(60)

   

if __name__ == "__main__":
    run()
