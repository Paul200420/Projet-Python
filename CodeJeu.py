#code renderer avant modif yanice :27 octobre
import pygame
from pygame import Rect
from enums.direction import Direction
import os


# 🎨 couleurs
GRID_BG    = (15, 15, 18)
ROOM_COL   = (40, 120, 200)
ENTRY_COL  = (220, 220, 220)
EXIT_COL   = (180, 220, 240)
DOOR_COL   = (0, 0, 0)
HIGHLIGHT  = (255, 255, 0)
PANEL_BG   = (250, 250, 250)
TEXT_COLOR = (0, 0, 0)


class Renderer:
   def __init__(self, game, window_width: int = 1200, window_height: int = 800, sidebar_ratio: float = 0.65):
       pygame.init()
       self.game = game


       self.w = window_width
       self.h = window_height


       self.sidebar_w = int(self.w * sidebar_ratio)       # partie droite
       self.grid_w = self.w - self.sidebar_w              # partie gauche


       rows = game.manor.rows
       cols = game.manor.cols


       self.cell_h = self.h / rows       # hauteur cellule pour remplir toute la fenêtre
       self.cell_w = self.grid_w / cols  # largeur cellule selon l'espace dispo pour la grille


       self.room_images = {}
       self.error_message = ""




       # Charger les icônes et les redimensionner automatiquement
       self.icon_size = int(self.cell_h *0.25 )  # Taille relative (40% de la hauteur de cellule)


       self.icons = {
           "steps": pygame.transform.smoothscale(
               pygame.image.load(os.path.join("assets", "icons", "steps.png")), (self.icon_size, self.icon_size)),
           "gold": pygame.transform.smoothscale(
               pygame.image.load(os.path.join("assets", "icons", "gold.png")), (self.icon_size, self.icon_size)),
           "gems": pygame.transform.smoothscale(
               pygame.image.load(os.path.join("assets", "icons", "gem.png")), (self.icon_size, self.icon_size)),
           "keys": pygame.transform.smoothscale(
               pygame.image.load(os.path.join("assets", "icons", "key.png")), (self.icon_size, self.icon_size)),
           "dice": pygame.transform.smoothscale(
               pygame.image.load(os.path.join("assets", "icons", "dice.png")), (self.icon_size, self.icon_size)),
       }




       self.screen = pygame.display.set_mode((self.w, self.h))
       pygame.display.set_caption("Blue Prince — Interface Graphique")




       self.font_tools_tilte = pygame.font.SysFont("arial", 30 , bold=True)
       self.font_tools = pygame.font.SysFont("arial", 20 )
       self.font_inventory = pygame.font.SysFont("arial", 25, bold=True)




       self.clock = pygame.time.Clock()
       self.current_dir = Direction.UP


   def draw(self):
       self.screen.fill(GRID_BG)
       self._draw_grid()
       self._draw_sidebar()
       pygame.display.flip()


##2.4 pas obliger, c'est pour afficher les couleurs et effets de chaque salle choisis
   def _wrap_text(self, text, font, max_width):
 
       if not text:
           return []
       words = text.split()
       lines, cur = [], ""
       for w in words:
           test = (cur + " " + w).strip()
           if font.size(test)[0] <= max_width:
               cur = test
           else:
               lines.append(cur)
               cur = w
       if cur:
           lines.append(cur)
       return [font.render(line, True, (0, 0, 0)) for line in lines]




   def _draw_sidebar(self):
       panel = Rect(self.grid_w, 0, self.sidebar_w, self.h)
       pygame.draw.rect(self.screen, PANEL_BG, panel)


       inv = self.game.player.inventory


       # --- Positions horizontales ---
       x_tools = self.grid_w + 20                         # à gauche du panneau
       x_inventory_icon = self.grid_w + self.sidebar_w - 50  # icône collée à droite
       x_inventory_value = x_inventory_icon + 40              # valeur à droite de l'icône


       # =========== TOOLS SECTION ===========
       y = 20
       tools_title = self.font_tools_tilte.render("TOOLS", True, TEXT_COLOR)
       self.screen.blit(tools_title, (x_tools, y))
       y += 50


       if inv.tools:
           for tool in inv.tools:
               name = tool.name.title().replace("_", " ")
               tool_text = self.font_tools.render(f"• {name}", True, TEXT_COLOR)
               self.screen.blit(tool_text, (x_tools, y))
               y += 20
       else:
           empty_text = self.font_tools.render("(no tools)", True, (120,120,120))
           self.screen.blit(empty_text, (x_tools, y))
           y += 20


       # =========== INVENTORY SECTION ===========
       y = 20
       icon_size = int(self.cell_h *0.25)


       stats = [
           ("steps", inv.steps),
           ("gold", inv.gold),
           ("gems", inv.gems),
           ("keys", inv.keys),
           ("dice", inv.dice),
       ]


       for icon_name, value in stats:
           icon_surface = pygame.transform.smoothscale(self.icons[icon_name], (icon_size, icon_size))


           value_text = self.font_inventory.render(str(value), True, TEXT_COLOR)
           value_width = value_text.get_width()
           value_x = x_inventory_icon - value_width - 10  # 10px d'espace avant l'icône


           # afficher le texte
           self.screen.blit(value_text, (value_x, y))


           # afficher l'icône à droite du texte
           self.screen.blit(icon_surface, (value_x + value_width + 10, y))


           y += icon_size + 10




       # === OBJETS DANS LA SALLE ===
       cell = self.game.manor.cell(self.game.player.pos)
       if cell.room and cell.room.contents:
           y += 20
           obj_title = self.font_tools_tilte.render("IN THIS ROOM:", True, TEXT_COLOR)
           self.screen.blit(obj_title, (x_tools, y))
           y += 30
           for obj in cell.room.contents:
               obj_text = self.font_tools.render(f"{obj.name} (press F to take)", True, TEXT_COLOR)
               self.screen.blit(obj_text, (x_tools, y))
               y += 20






       # =========== ERROR MESSAGE ===========    
       if self.error_message:
           error_font = pygame.font.SysFont("arial", 15, bold=True)
           error_text = error_font.render(self.error_message, True, (200, 0, 0))
           # Affichage à 20px du bas de la sidebar
           self.screen.blit(error_text, (self.grid_w + 20, self.h - 30))
 


   def _draw_grid(self):
       m = self.game.manor
       for r in range(m.rows):
           for c in range(m.cols):
               x = int(c * self.cell_w)
               # y = int((m.rows - 1 - r) * self.cell_h)  # origine visuelle en bas
               y = int(r * self.cell_h)




               rect = Rect(x, y, int(self.cell_w), int(self.cell_h))
               pygame.draw.rect(self.screen, (35, 35, 42), rect, border_radius=6)


               cell = m.grid[r][c]


               if cell.room:
                   # Charger l'image si pas encore dans le cache
                   if cell.room.image_path not in self.room_images:
                       img = pygame.image.load(cell.room.image_path).convert_alpha()
                       img = pygame.transform.smoothscale(img, (int(self.cell_w), int(self.cell_h)))
                       self.room_images[cell.room.image_path] = img


                   # Récupérer l'image
                   room_img = self.room_images[cell.room.image_path]


                   # Dessiner l'image dans la cellule
                   self.screen.blit(room_img, (x, y))


                   name = cell.room.name.upper()
                   # txt = self.font.render(name, True, (30, 30, 30))
                   txt = self.font_tools.render(name, True, (30, 30, 30))


                   self.screen.blit(txt, (x + self.cell_w * 0.08, y + self.cell_h * 0.08))


               # Portes
               for d in cell.doors.keys():
                   tab_w = int(self.cell_w * 0.35)
                   tab_h = int(self.cell_h * 0.24)
                   edge_t = max(2, int(min(self.cell_w, self.cell_h) * 0.06))


                   if d is Direction.UP:
                       px = int(x + self.cell_w/2 - tab_w/2)
                       py = int(y - edge_t)
                       pygame.draw.rect(self.screen, DOOR_COL, Rect(px, py, tab_w, edge_t + 2))


                   if d is Direction.DOWN:
                       px = int(x + self.cell_w/2 - tab_w/2)
                       py = int(y + self.cell_h - 2)
                       pygame.draw.rect(self.screen, DOOR_COL, Rect(px, py, tab_w, edge_t + 2))


                   if d is Direction.LEFT:
                       px = int(x - edge_t)
                       py = int(y + self.cell_h/2 - tab_h/2)
                       pygame.draw.rect(self.screen, DOOR_COL, Rect(px, py, edge_t + 2, tab_h))


                   if d is Direction.RIGHT:
                       px = int(x + self.cell_w - 2)
                       py = int(y + self.cell_h/2 - tab_h/2)
                       pygame.draw.rect(self.screen, DOOR_COL, Rect(px, py, edge_t + 2, tab_h))






       pr, pc = self.game.player.pos.r, self.game.player.pos.c
       x = int(pc * self.cell_w)
       y = int(pr * self.cell_h)  # <-- la ligne clé
       cell_rect = Rect(x, y, int(self.cell_w), int(self.cell_h))


       # Bordure normale
       pygame.draw.rect(self.screen, (255, 255, 255), cell_rect, width=3)


       # Accentuation selon la direction choisie (si tu l’as ajoutée)
       accent_thickness = 8
       if self.current_dir == Direction.UP:
           pygame.draw.line(self.screen, (255, 255, 255), (x, y), (x + self.cell_w, y), width=accent_thickness)
       elif self.current_dir == Direction.DOWN:
           pygame.draw.line(self.screen, (255, 255, 255), (x, y + self.cell_h), (x + self.cell_w, y + self.cell_h), width=accent_thickness)
       elif self.current_dir == Direction.LEFT:
           pygame.draw.line(self.screen, (255, 255, 255), (x, y), (x, y + self.cell_h), width=accent_thickness)
       elif self.current_dir == Direction.RIGHT:
           pygame.draw.line(self.screen, (255, 255, 255), (x + self.cell_w, y), (x + self.cell_w, y + self.cell_h), width=accent_thickness)








   def _action_link(self, text: str, x: int, y: int):
       surf = self.font.render(text, True, (60, 100, 200))
       self.screen.blit(surf, (x, y))


#code game module open_or_place yanice: avant modif paul pour 2.6:
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
            cur_cell.doors[d] = Door(_lock=LockLevel.UNLOCKED, _leads_to=nxt)

        # Crée la porte retour si autorisée
        back = {Direction.UP: Direction.DOWN, Direction.DOWN: Direction.UP,
                Direction.LEFT: Direction.RIGHT, Direction.RIGHT: Direction.LEFT}[d]
        if back not in tgt_cell.doors and back in tgt_cell.room.possible_doors:
            tgt_cell.doors[back] = Door(_lock=LockLevel.UNLOCKED, _leads_to=cur)

        return True