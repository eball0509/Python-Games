"""SettingsScene (R11, stretch): master volume control plus a
controls reference for all three games, reachable from the main menu.

pauseable = False: ESC here returns straight to the main menu instead
of opening the shared pause overlay -- same reasoning as MenuScene,
pausing a settings screen doesn't mean anything.
"""

import pygame
from core.scene import Scene

VOLUME_STEP = 0.05

CONTROLS = [
    ("Asteroids", ["Arrows/WASD: move", "Q/E: rotate", "Space: shoot", "ESC: pause"]),
    ("GhostBusters", ["Arrows: move", "Up: jump", "Space: shoot", "G: grenade", "ESC: pause"]),
    ("Salvage Run", ["Arrows/WASD: move", "ESC: pause"]),
    ("Pause Overlay", ["ESC: resume", "M: return to menu", "Q: quit"]),
]


class SettingsScene(Scene):
    pauseable = False

    def __init__(self, manager, app):
        super().__init__(manager)
        self.app = app
        self.assets = app.assets

        self.title_font = self.assets.get_font(None, 36)
        self.label_font = self.assets.get_font(None, 22)
        self.game_font = self.assets.get_font(None, 20)
        self.bind_font = self.assets.get_font(None, 16)
        self.hint_font = self.assets.get_font(None, 16)

    def handle_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                from scenes.menu_scene import build_menu_scene
                self.manager.switch_to(build_menu_scene(self.manager, self.app))
                return
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.assets.set_master_volume(self.assets.master_volume - VOLUME_STEP)
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self.assets.set_master_volume(self.assets.master_volume + VOLUME_STEP)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((15, 15, 25))

        title = self.title_font.render("Settings", True, (255, 255, 255))
        surface.blit(title, (40, 30))

        label = self.label_font.render("Master Volume", True, (220, 220, 230))
        surface.blit(label, (40, 90))

        bar_x, bar_y, bar_w, bar_h = 40, 125, 300, 24
        pygame.draw.rect(surface, (50, 50, 65), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        fill_w = int(bar_w * self.assets.master_volume)
        if fill_w > 0:
            pygame.draw.rect(surface, (37, 99, 235), (bar_x, bar_y, fill_w, bar_h), border_radius=6)
        pygame.draw.rect(surface, (150, 150, 165), (bar_x, bar_y, bar_w, bar_h), width=2, border_radius=6)

        pct_text = self.label_font.render(f"{int(round(self.assets.master_volume * 100))}%", True, (255, 255, 255))
        surface.blit(pct_text, (bar_x + bar_w + 16, bar_y - 2))

        hint = self.hint_font.render("Left/Right (or A/D) to adjust -- saved automatically", True, (150, 150, 160))
        surface.blit(hint, (40, 160))

        controls_title = self.label_font.render("Controls", True, (220, 220, 230))
        surface.blit(controls_title, (40, 210))

        col_x = 40
        col_y = 245
        col_width = surface.get_width() // 2 - 60
        for i, (game_name, bindings) in enumerate(CONTROLS):
            x = col_x + (i % 2) * (col_width + 40)
            y = col_y + (i // 2) * 140
            name_surf = self.game_font.render(game_name, True, (250, 210, 90))
            surface.blit(name_surf, (x, y))
            for j, binding in enumerate(bindings):
                b_surf = self.bind_font.render(binding, True, (200, 200, 210))
                surface.blit(b_surf, (x, y + 28 + j * 20))

        back_hint = self.hint_font.render("ESC: back to menu", True, (150, 150, 160))
        surface.blit(back_hint, (40, surface.get_height() - 40))