import pygame
from pygame import Rect
from enums.direction import Direction
from models.coord import Coord
from objects.interactive import Vendor
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
    def __init__(self, game, window_width: int = 1200, window_height: int = 1100, sidebar_ratio: float = 0.58):
        pygame.init()
        self.game = game

        self.w = window_width
        self.h = window_height

        # partie droite / partie gauche
        self.sidebar_w = int(self.w * sidebar_ratio)   # panneau d'infos (blanc)
        self.grid_w = self.w - self.sidebar_w          # zone de grille (noir)

        rows = game.manor.rows
        cols = game.manor.cols

        # on calcule la taille brute
        raw_cell_h = self.h / rows
        raw_cell_w = self.grid_w / cols

        # on force des cases carrées
        self.cell_size = min(raw_cell_h, raw_cell_w)

        # pour centrer verticalement la grille si jamais la hauteur ne tombe pas pile
        used_grid_height = self.cell_size * rows
        self.grid_y_offset = (self.h - used_grid_height) // 2

        self.room_images = {}
        self.error_message = ""

        # Charger les icônes et les redimensionner automatiquement
        self.icon_size = int(self.cell_size * 0.25)  # Taille relative

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
            "small_business_fragments": pygame.transform.smoothscale(
                pygame.image.load(os.path.join("assets", "icons", "small-business.png")), (self.icon_size, self.icon_size)),
        }

        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Blue Prince — Interface Graphique")

        self.font_tools_tilte = pygame.font.SysFont("arial", 30, bold=True)
        self.font_tools = pygame.font.SysFont("arial", 20)
        self.font_inventory = pygame.font.SysFont("arial", 25, bold=True)

        self.clock = pygame.time.Clock()
        self.current_dir = Direction.UP
        self.selected_room_index = 0  # Index de la pièce sélectionnée

    def draw(self):
        # Nettoyer le cache d'images si nécessaire
        if not self.game.current_room_choices:
            # Conserver uniquement les images des pièces placées et les previews
            kept_images = {}
            for path, img in self.room_images.items():
                # Garder les images de preview
                if path.startswith("preview_"):
                    continue
                # Vérifier si l'image est utilisée dans le manoir
                for r in range(self.game.manor.rows):
                    for c in range(self.game.manor.cols):
                        cell = self.game.manor.cell(Coord(r, c))
                        if cell.room and cell.room.image_path == path:
                            kept_images[path] = img
                            break

            # Mettre à jour le cache d'images
            self.room_images = kept_images

        self.screen.fill(GRID_BG)
        self._draw_grid()
        self._draw_sidebar()

        # Afficher l'interface de sélection des pièces si nécessaire
        if self.game.current_room_choices:
            self._draw_room_selection()

        pygame.display.flip()

    def _draw_room_selection(self):
        # Fond semi-transparent
        s = pygame.Surface((self.w, self.h))
        s.set_alpha(128)
        s.fill((0, 0, 0))
        self.screen.blit(s, (0, 0))

        # Positions des cartes de pièce
        card_width = 200
        card_height = 300
        card_spacing = 50
        total_width = (card_width * 3) + (card_spacing * 2)
        start_x = (self.w - total_width) // 2
        start_y = (self.h - card_height) // 2

        for i, room in enumerate(self.game.current_room_choices):
            x = start_x + (i * (card_width + card_spacing))

            # Dessiner le fond de la carte
            pygame.draw.rect(self.screen, (255, 255, 255), (x, start_y, card_width, card_height))
            pygame.draw.rect(
                self.screen,
                room._couleur.value if hasattr(room._couleur, 'value') else room._couleur,
                (x + 5, start_y + 5, card_width - 10, card_height - 10)
            )

            # Nom de la pièce
            room_name = self.font_inventory.render(room.name, True, (255, 255, 255))
            name_x = x + (card_width - room_name.get_width()) // 2
            self.screen.blit(room_name, (name_x, start_y + 20))

            # Charger l'image de la pièce si disponible
            if hasattr(room, 'image_path') and room.image_path:
                preview_key = f"preview_{room.image_path}"
                if preview_key not in self.room_images:
                    try:
                        img = pygame.image.load(room.image_path).convert_alpha()
                        img = pygame.transform.smoothscale(img, (card_width - 20, card_width - 20))
                        self.room_images[preview_key] = img
                    except (pygame.error, FileNotFoundError):
                        continue

                room_img = self.room_images[preview_key]
                img_x = x + 10
                img_y = start_y + 60
                self.screen.blit(room_img, (img_x, img_y))

            # Texte de sélection
            if i == self.selected_room_index:
                select_text = self.font_tools.render("Press O to choose", True, (255, 255, 0))
            else:
                select_text = self.font_tools.render("Use ← → to select", True, (255, 255, 255))
            text_x = x + (card_width - select_text.get_width()) // 2
            self.screen.blit(select_text, (text_x, start_y + card_height - 40))

        # Texte pour le dé
        if self.game.player.inventory.dice > 0:
            dice_text = self.font_tools.render("Press R to reroll", True, (255, 255, 255))
            dice_x = (self.w - dice_text.get_width()) // 2
            self.screen.blit(dice_text, (dice_x, start_y + card_height + 20))

    # === Helper pour couper le texte d'effet proprement ===
    def _wrap_text(self, text, font, max_width):
        """Retourne une liste de surfaces texte wrapées pour ne pas dépasser max_width."""
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
      
        # largeur réellement utilisée par la grille (cases carrées)
        used_grid_w = int(self.cell_size * self.game.manor.cols)
        
        # on fait commencer l'interface blanc juste après ces cases graphiques du jeu
        panel = Rect(used_grid_w, 0, self.w - used_grid_w, self.h)
        pygame.draw.rect(self.screen, PANEL_BG, panel)

        inv = self.game.player.inventory

        # et on recalcule les positions de texte à partir de cette vraie bordure colonne x
        x_left = used_grid_w + 20
        x_icon = self.w - 50

        # =========== INVENTAIRE (icônes à droite) ===========
        y = 20
        icon_size = int(self.cell_size * 0.25)
        stats = [
            ("steps", inv.steps),
            ("gold", inv.gold),
            ("gems", inv.gems),
            ("keys", inv.keys),
            ("dice", inv.dice),
            ("small_business_fragments", inv.small_business_count),

        ]
        for icon_name, value in stats:
            icon_surface = pygame.transform.smoothscale(self.icons[icon_name], (icon_size, icon_size))
            value_text = self.font_inventory.render(str(value), True, TEXT_COLOR)
            value_w = value_text.get_width()
            value_x = x_icon - value_w - 10
            self.screen.blit(value_text, (value_x, y))
            self.screen.blit(icon_surface, (value_x + value_w + 10, y))
            y += icon_size + 10

        # =========== OUTILS ===========
        y_tools = 20
        tools_title = self.font_tools_tilte.render("TOOLS", True, TEXT_COLOR)
        self.screen.blit(tools_title, (x_left, y_tools))
        y_tools += 50
        if inv.tools:
            for tool in inv.tools:
                name = tool.name.title().replace("_", " ")
                line = self.font_tools.render(f"• {name}", True, TEXT_COLOR)
                self.screen.blit(line, (x_left, y_tools))
                y_tools += 20
        else:
            self.screen.blit(self.font_tools.render("(no tools)", True, (120, 120, 120)), (x_left, y_tools))
            y_tools += 20

        # =========== INFO PIÈCE ACTUELLE ===========
        cell = self.game.manor.cell(self.game.player.pos)
        room = cell.room
        y_info = max(y, y_tools) + 20

        if room:
            # Titre
            title = self.font_tools_tilte.render("PIÈCE ACTUELLE", True, TEXT_COLOR)
            self.screen.blit(title, (x_left, y_info))
            y_info += 36

            # Nom
            self.screen.blit(self.font_tools.render(f"Nom : {room.name}", True, TEXT_COLOR), (x_left, y_info))
            y_info += 22

            # Couleur (si disponible)
            couleur = getattr(room, "_couleur", None)
            if couleur is not None:
                try:
                    couleur_label = couleur.name.title()
                except Exception:
                    couleur_label = str(couleur)
                self.screen.blit(self.font_tools.render(f"Couleur : {couleur_label}", True, TEXT_COLOR), (x_left, y_info))
                y_info += 22

            # Effet (si disponible)
            effet_txt = getattr(room, "effet_texte", "")
            if effet_txt:
                self.screen.blit(self.font_tools.render("Effet :", True, TEXT_COLOR), (x_left, y_info))
                y_info += 22
                max_w = self.sidebar_w - 40
                for line_surf in self._wrap_text(effet_txt, self.font_tools, max_w):
                    self.screen.blit(line_surf, (x_left, y_info))
                    y_info += 20

        # =========== OBJETS DANS LA SALLE ===========
                # =========== OBJETS DANS LA SALLE ===========
        if room and room.contents:
            y_info += 20
            self.screen.blit(self.font_tools_tilte.render("IN THIS ROOM:", True, TEXT_COLOR), (x_left, y_info))
            y_info += 30

            for obj in room.contents:
                # texte par défaut
                line = f"{obj.name} (press F to take)"

                # si c'est le vendeur, on change la ligne principale
                if isinstance(obj, Vendor):
                    line = "Comptoir du magasin (appuyez 1–5 pour acheter)"

                # on affiche la ligne principale
                self.screen.blit(self.font_tools.render(line, True, TEXT_COLOR), (x_left, y_info))
                y_info += 20

                # si c'est le vendeur, on affiche aussi son catalogue juste dessous
                if isinstance(obj, Vendor):
                    # on suppose que Vendor a une méthode get_catalog_lines()
                    for subline in obj.get_catalog_lines():
                        self.screen.blit(self.font_tools.render(subline, True, TEXT_COLOR), (x_left + 15, y_info))
                        y_info += 18


        # =========== MESSAGE D'ERREUR ===========
        if self.error_message:
            err_font = pygame.font.SysFont("arial", 15, bold=True)
            err = err_font.render(self.error_message, True, (200, 0, 0))
            self.screen.blit(err, (self.grid_w + 20, self.h - 30))

    def _draw_grid(self):
        m = self.game.manor
        for r in range(m.rows):
            for c in range(m.cols):
                x = int(c * self.cell_size)
                y = int(self.grid_y_offset + r * self.cell_size)

                rect = Rect(x, y, int(self.cell_size), int(self.cell_size))
                pygame.draw.rect(self.screen, (35, 35, 42), rect, border_radius=6)

                cell = m.grid[r][c]

                if cell.room:
                    # Charger l'image si pas encore dans le cache
                    if hasattr(cell.room, 'image_path') and cell.room.image_path:
                        if cell.room.image_path not in self.room_images:
                            try:
                                img = pygame.image.load(cell.room.image_path).convert_alpha()
                                img = pygame.transform.smoothscale(img, (int(self.cell_size), int(self.cell_size)))
                                self.room_images[cell.room.image_path] = img
                            except (pygame.error, FileNotFoundError):
                                # En cas d'erreur de chargement, on utilise une couleur de fond
                                color = cell.room._couleur.value if hasattr(cell.room._couleur, 'value') else cell.room._couleur
                                pygame.draw.rect(self.screen, color, rect)
                                continue

                        # Récupérer et afficher l'image
                        room_img = self.room_images[cell.room.image_path]
                        self.screen.blit(room_img, (x, y))
                    else:
                        # Si pas d'image, utiliser la couleur de la pièce
                        color = cell.room._couleur.value if hasattr(cell.room._couleur, 'value') else cell.room._couleur
                        pygame.draw.rect(self.screen, color, rect)

                    name = cell.room.name.upper()
                    txt = self.font_tools.render(name, True, (30, 30, 30))
                    self.screen.blit(txt, (x + self.cell_size * 0.08, y + self.cell_size * 0.08))

                # Portes
                for d in cell.doors.keys():
                    tab_w = int(self.cell_size * 0.35)
                    tab_h = int(self.cell_size * 0.24)
                    edge_t = max(2, int(self.cell_size * 0.06))

                    if d is Direction.UP:
                        px = int(x + self.cell_size / 2 - tab_w / 2)
                        py = int(y - edge_t)
                        pygame.draw.rect(self.screen, DOOR_COL, Rect(px, py, tab_w, edge_t + 2))

                    if d is Direction.DOWN:
                        px = int(x + self.cell_size / 2 - tab_w / 2)
                        py = int(y + self.cell_size - 2)
                        pygame.draw.rect(self.screen, DOOR_COL, Rect(px, py, tab_w, edge_t + 2))

                    if d is Direction.LEFT:
                        px = int(x - edge_t)
                        py = int(y + self.cell_size / 2 - tab_h / 2)
                        pygame.draw.rect(self.screen, DOOR_COL, Rect(px, py, edge_t + 2, tab_h))

                    if d is Direction.RIGHT:
                        px = int(x + self.cell_size - 2)
                        py = int(y + self.cell_size / 2 - tab_h / 2)
                        pygame.draw.rect(self.screen, DOOR_COL, Rect(px, py, edge_t + 2, tab_h))

        # position du joueur
        pr, pc = self.game.player.pos.r, self.game.player.pos.c
        x = int(pc * self.cell_size)
        y = int(self.grid_y_offset + pr * self.cell_size)
        cell_rect = Rect(x, y, int(self.cell_size), int(self.cell_size))

        # Bordure normale
        pygame.draw.rect(self.screen, (255, 255, 255), cell_rect, width=3)

        # Accentuation selon la direction choisie
        accent_thickness = 8
        if self.current_dir == Direction.UP:
            pygame.draw.line(self.screen, (255, 255, 255), (x, y), (x + self.cell_size, y), width=accent_thickness)
        elif self.current_dir == Direction.DOWN:
            pygame.draw.line(self.screen, (255, 255, 255), (x, y + self.cell_size), (x + self.cell_size, y + self.cell_size), width=accent_thickness)
        elif self.current_dir == Direction.LEFT:
            pygame.draw.line(self.screen, (255, 255, 255), (x, y), (x, y + self.cell_size), width=accent_thickness)
        elif self.current_dir == Direction.RIGHT:
            pygame.draw.line(self.screen, (255, 255, 255), (x + self.cell_size, y), (x + self.cell_size, y + self.cell_size), width=accent_thickness)

    def _action_link(self, text: str, x: int, y: int):
        # Utilise une police existante (font_tools) pour éviter les erreurs
        surf = self.font_tools.render(text, True, (60, 100, 200))
        self.screen.blit(surf, (x, y))
