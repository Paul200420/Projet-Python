import pygame, sys
from world.manor import Manor
from game.game import Game
from enums.direction import Direction
from ui.renderer import Renderer

from objects.permanent import ShovelObj, MetalDetectorObj
from objects.consumable import Apple, Cake
from objects.interactive import Chest, Vendor  #: Vendor pour le shop dans kitchen


def run():
    manor = Manor()
    game = Game(manor)

    # Placer des objets permanents dans la salle de départ
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

                # --- Gestion de la sélection des pièces (quand un tirage est affiché) ---
                if game.current_room_choices:
                    # Pendant la sélection, on utilise ←/→ pour naviguer, 'O' pour valider, 'R' pour relancer.
                    if event.key == pygame.K_LEFT:
                        renderer.selected_room_index = (renderer.selected_room_index - 1) % len(game.current_room_choices)
                    elif event.key == pygame.K_RIGHT:
                        renderer.selected_room_index = (renderer.selected_room_index + 1) % len(game.current_room_choices)
                    elif event.key == pygame.K_o:
                        # Sauvegarder la direction avant de choisir la pièce
                        saved_direction = game.current_draw_direction
                        idx = renderer.selected_room_index

                        try:
                            room_to_place = game.current_room_choices[idx]
                        except Exception:
                            room_to_place = None

                        if room_to_place is None:
                            renderer.error_message = "Erreur : aucune pièce sélectionnée."
                            break
                        if game.player.inventory.gems < room_to_place.gem_cost:
                            renderer.error_message = f"Pas assez de gemmes (coût : {room_to_place.gem_cost})."
                            break
                        if saved_direction not in room_to_place.possible_doors:
                            renderer.error_message = "Cette pièce n'a pas de porte dans cette direction."
                            break

                        # --- Valider le choix ---
                        placed = game.choose_room(idx)
                        if not placed:
                            renderer.error_message = "Choix impossible."
                            break

                        # On vide le choix manuellement ici
                        game.current_room_choices = []
                        game.current_draw_position = None
                        game.current_draw_direction = None

                        # Ensuite, on crée la porte correspondante
                        renderer.selected_room_index = 0
                        if saved_direction is not None:
                            game.open_or_place(saved_direction)

                        renderer.error_message = "Pièce placée et porte ouverte."
                        renderer.draw()
                        break  # <-- empêche une double action dans la même frame

                    elif event.key == pygame.K_r:
                        # Retirage avec un dé (R)
                        if game.player.inventory.dice > 0:
                            if game.redraw_rooms():
                                renderer.error_message = "Nouvelles pièces tirées (-1 dé)"
                                renderer.selected_room_index = 0
                            else:
                                renderer.error_message = "Erreur lors du retirage"
                        else:
                            renderer.error_message = "Vous n'avez plus de dés disponibles"
                        break

                    # Pendant le choix, on ignore le reste (pas de changement de direction).
                    continue

                # --- 2.5: Sélection de la direction (ZQSD + flèches) ---
                if event.key in (pygame.K_z, pygame.K_UP):
                    current_dir = Direction.UP
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    current_dir = Direction.DOWN
                elif event.key in (pygame.K_q, pygame.K_LEFT):
                    current_dir = Direction.LEFT
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    current_dir = Direction.RIGHT

                # --- 2.5: ESPACE = ouvrir/placer la porte dans la direction choisie ---
                elif event.key == pygame.K_SPACE:
                    # Empêcher un re-tirage immédiat après un choix
                    if game.current_draw_position is None and not game.current_room_choices:
                        nxt = game._neighbor(game.player.pos, current_dir)
                        if nxt is None:
                            renderer.error_message = "Impossible : mur (hors du manoir)."
                        else:
                            ok = game.open_or_place(current_dir)
                            renderer.error_message = "Porte ouverte." if ok else "Impossible d'ouvrir/placer la porte."
                    else:
                        renderer.error_message = "Une salle vient d'être placée. Déplacez-vous avant de continuer."

                # --- 2.5: ENTRÉE = se déplacer via porte ouverte (consomme 1 pas) ---
                elif event.key == pygame.K_RETURN:
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
                                if avant <= 0:
                                    renderer.error_message = "Vous n'avez plus de pas."
                                else:
                                    if not door.can_open(game.player.inventory):
                                        renderer.error_message = "Porte verrouillée : il faut une clé (kit OK pour niveau 1)."
                                    else:
                                        renderer.error_message = "Déplacement impossible."
                            else:
                                renderer.error_message = f"Déplacement réussi (-1 pas). Pas restants : {game.player.inventory.steps}"

                                if game.reached_exit():
                                    renderer.error_message = "🎉 Vous avez atteint l'antichambre !"
                                    renderer.draw()
                                    pygame.time.wait(1800)
                                    pygame.quit(); sys.exit(0)

                # --- Ramasser / interagir avec l'objet en tête de salle ---
                elif event.key == pygame.K_f:
                    msg = game.pick_up_here()
                    if msg:
                        renderer.error_message = msg

                # --- 1..5 : achat dans le shop de la salle courante ---
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                    cell = game.manor.cell(game.player.pos)
                    if cell.room and cell.room.contents:
                        # on cherche un Vendor dans cette salle
                        vendor = next((o for o in cell.room.contents if isinstance(o, Vendor)), None)
                        if vendor:
                            idx = int(event.unicode) 
                            msg = vendor.buy_item(game, idx)
                            renderer.error_message = msg

        renderer.current_dir = current_dir
        renderer.draw()
        renderer.clock.tick(60)
        
        # === Vérification de la défaite ===
        if game.player.inventory.steps <= 0:
            renderer.error_message = "Vous n'avez plus de pas... Partie terminée."
            renderer.draw()
            pygame.time.wait(2000)
            pygame.quit()
            sys.exit(0)



if __name__ == "__main__":
    run()
