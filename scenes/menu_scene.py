"""Main menu / game-select screen (R4).

build_menu_scene() is the one place that lists every playable entry.
Asteroids now points at the real AsteroidsScene (R5). GhostBusters and
Salvage Run still point at ComingSoonScene until R6/R7 land -- swap
those the same way once each is ported/built.
"""

from functools import partial
import pygame
from core.scene import Scene
from scenes.placeholder_scene import ComingSoonScene
from scenes.asteroids_scene import AsteroidsScene


def build_menu_scene(manager, app):
    entries = [
        ("Asteroids", "Classic space shooter", lambda m, a: AsteroidsScene(m, a)),
        ("GhostBusters", "Platformer w/ parallax", partial(ComingSoonScene, game_name="GhostBusters")),
        ("Salvage Run", "NEW: mining run", partial(ComingSoonScene, game_name="Salvage Run")),
        ("Settings", "Volume & controls", partial(ComingSoonScene, game_name="Settings")),
    ]
    return MenuScene(manager, app, entries)


class MenuScene(Scene):
    """entries: list of (label, subtitle, scene_factory).
    scene_factory(manager, app) -> Scene, called when that entry is selected.
    """

    ROW_HEIGHT = 70
    ROW_GAP = 16
    TOP_MARGIN = 110

    def __init__(self, manager, app, entries):
        super().__init__(manager)
        self.app = app
        self.entries = entries
        self.selected = 0

        self.title_font = app.assets.get_font(None, 40)
        self.item_font = app.assets.get_font(None, 26)
        self.sub_font = app.assets.get_font(None, 16)
        self.hint_font = app.assets.get_font(None, 16)

    def handle_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.entries)
            elif event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.entries)
            elif event.key == pygame.K_RETURN:
                self._select_current()
            elif event.key == pygame.K_ESCAPE:
                self.app.running = False

    def _select_current(self):
        _label, _subtitle, scene_factory = self.entries[self.selected]
        new_scene = scene_factory(self.manager, self.app)
        self.manager.switch_to(new_scene)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((15, 15, 25))

        title_surf = self.title_font.render("Salvage Arcade", True, (255, 255, 255))
        surface.blit(title_surf, (40, 30))

        for i, (label, subtitle, _factory) in enumerate(self.entries):
            y = self.TOP_MARGIN + i * (self.ROW_HEIGHT + self.ROW_GAP)
            rect = pygame.Rect(40, y, surface.get_width() - 80, self.ROW_HEIGHT)
            is_selected = (i == self.selected)

            fill = (37, 99, 235) if is_selected else (40, 40, 55)
            text_color = (255, 255, 255) if is_selected else (200, 200, 210)
            pygame.draw.rect(surface, fill, rect, border_radius=6)

            label_surf = self.item_font.render(label, True, text_color)
            surface.blit(label_surf, (rect.x + 16, rect.y + 8))
            if subtitle:
                sub_surf = self.sub_font.render(subtitle, True, text_color)
                surface.blit(sub_surf, (rect.x + 16, rect.y + 38))

        hint_surf = self.hint_font.render(
            "Up/Down = navigate   Enter = select   ESC = quit", True, (150, 150, 160)
        )
        surface.blit(hint_surf, (40, surface.get_height() - 40))