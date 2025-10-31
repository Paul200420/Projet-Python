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

        self.sidebar_w = int(self.w * sidebar_ratio)
        self.grid_w = self.w - self.sidebar_w

        rows = game.manor.rows
        cols = game.manor.cols

        self.cell_h = self.h / rows
        self.cell_w = self.grid_w / cols

        self.room_images = {}
        self.error_message = ""
        self.message_timer = 0  # ⬅️ pour message temporisé

        self.icon_size = int(self.cell_h * 0.25)

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

        self.font_tools_tilte = pygame.font.SysFont("arial", 30, bold=True)
        self.font_tools = pygame.font.SysFont("arial", 20)
        self.font_inventory = pygame.font.SysFont("arial", 25, bold=True)
        self.font_message = pygame.font.SysFont("arial", 18, bold=True)

        self.clock = pygame.time.Clock()
        self.current_dir = Direction.UP

    def draw(self):
        self.screen.fill(GRID_BG)
        self._draw_grid()
        self._draw_sidebar()

        # 🔥 Afficher message si existe
        if self.error_message:
            surf = self.font_message.render(self.error_message, True, (200, 40, 40))
            self.screen.blit(surf, (20, self.h - 30))

            self.message_timer -= 1
            if self.message_timer <= 0:
                self.error_message = ""

        pygame.display.flip()

    def show_message(self, msg: str):
        self.error_message = msg
        self.message_timer = 180  # ~3 sec

    # === Helper texte multiline ===
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

        # --- colonnes x ---
        x_left = self.grid_w + 20
        x_icon = self.grid_w + self.sidebar_w - 50

        # ===== INVENTAIRE =====
        y = 20
        icon_size = int(self.cell_h * 0.25)
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
            value_w = value_text.get_width()
            value_x = x_icon - value_w - 10
            self.screen.blit(value_text, (value_x, y))
            self.screen.blit(icon_surface, (value_x + value_w + 10, y))
            y += icon_size + 10

        # ===== OUTILS =====
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

        # ===== ROOM INFO =====
        cell = self.game.manor.cell(self.game.player.pos)
        room = cell.room
        y_info = max(y, y_tools) + 20

        if room:
            title = self.font_tools_tilte.render("PIÈCE ACTUELLE", True, TEXT_COLOR)
            self.screen.blit(title, (x_left, y_info)); y_info += 36

            self.screen.blit(self.font_tools.render(f"Nom : {room.name}", True, TEXT_COLOR), (x_left, y_info))
            y_info += 22

            couleur = getattr(room, "couleur", None)
            if couleur is not None:
                try:
                    couleur_label = couleur.name.title()
                except:
                    couleur_label = str(couleur)
                self.screen.blit(self.font_tools.render(f"Couleur : {couleur_label}", True, TEXT_COLOR), (x_left, y_info))
                y_info += 22

            effet_txt = getattr(room, "effet_texte", "")
            if effet_txt:
                self.screen.blit(self.font_tools.render("Effet :", True, TEXT_COLOR), (x_left, y_info))
                y_info += 22
                max_w = self.sidebar_w - 40
                for line_surf in self._wrap_text(effet_txt, self.font_tools, max_w):
                    self.screen.blit(line_surf, (x_left, y_info))
                    y_info += 20

        # ===== OBJETS DANS LA PIÈCE =====
        if room and room.contents:
            y_info += 20
            self.screen.blit(self.font_tools_tilte.render("IN THIS ROOM:", True, TEXT_COLOR), (x_left, y_info))
            y_info += 30
            for obj in room.contents:
                self.screen.blit(self.font_tools.render(f"{obj.name} (press F to interact)", True, TEXT_COLOR), (x_left, y_info))
                y_info += 20

    def _draw_grid(self):
        m = self.game.manor
        for r in range(m.rows):
            for c in range(m.cols):
                x = int(c * self.cell_w)
                y = int(r * self.cell_h)

                rect = Rect(x, y, int(self.cell_w), int(self.cell_h))
                pygame.draw.rect(self.screen, (35, 35, 42), rect, border_radius=6)

                cell = m.grid[r][c]

                if cell.room:
                    if cell.room.image_path not in self.room_images:
                        img = pygame.image.load(cell.room.image_path).convert_alpha()
                        img = pygame.transform.smoothscale(img, (int(self.cell_w), int(self.cell_h)))
                        self.room_images[cell.room.image_path] = img

                    room_img = self.room_images[cell.room.image_path]
                    self.screen.blit(room_img, (x, y))

                    name = cell.room.name.upper()
                    txt = self.font_tools.render(name, True, (30, 30, 30))
                    self.screen.blit(txt, (x + self.cell_w * 0.08, y + self.cell_h * 0.08))

                # DOORS
                for d in cell.doors.keys():
                    tab_w = int(self.cell_w * 0.35)
                    tab_h = int(self.cell_h * 0.24)
                    edge_t = max(2, int(min(self.cell_w, self.cell_h) * 0.06))

                    if d is Direction.UP:
                        pygame.draw.rect(self.screen, DOOR_COL, Rect(x + self.cell_w/2 - tab_w/2, y - edge_t, tab_w, edge_t + 2))
                    if d is Direction.DOWN:
                        pygame.draw.rect(self.screen, DOOR_COL, Rect(x + self.cell_w/2 - tab_w/2, y + self.cell_h - 2, tab_w, edge_t + 2))
                    if d is Direction.LEFT:
                        pygame.draw.rect(self.screen, DOOR_COL, Rect(x - edge_t, y + self.cell_h/2 - tab_h/2, edge_t + 2, tab_h))
                    if d is Direction.RIGHT:
                        pygame.draw.rect(self.screen, DOOR_COL, Rect(x + self.cell_w - 2, y + self.cell_h/2 - tab_h/2, edge_t + 2, tab_h))

        # PLAYER
        pr, pc = self.game.player.pos.r, self.game.player.pos.c
        x = int(pc * self.cell_w)
        y = int(pr * self.cell_h)
        cell_rect = Rect(x, y, int(self.cell_w), int(self.cell_h))

        pygame.draw.rect(self.screen, (255, 255, 255), cell_rect, width=3)

        accent = 8
        if self.current_dir == Direction.UP:
            pygame.draw.line(self.screen, (255, 255, 255), (x, y), (x + self.cell_w, y), width=accent)
        elif self.current_dir == Direction.DOWN:
            pygame.draw.line(self.screen, (255, 255, 255), (x, y + self.cell_h), (x + self.cell_w, y + self.cell_h), width=accent)
        elif self.current_dir == Direction.LEFT:
            pygame.draw.line(self.screen, (255, 255, 255), (x, y), (x, y + self.cell_h), width=accent)
        elif self.current_dir == Direction.RIGHT:
            pygame.draw.line(self.screen, (255, 255, 255), (x + self.cell_w, y), (x + self.cell_w, y + self.cell_h), width=accent)
