"""Stand-in for a game that hasn't been ported/built yet.

The menu (R4) needs something to switch to for every entry, but
AsteroidsScene/GhostBustersScene/SalvageRunScene don't exist until
R5/R6/R7 are done. This lets the menu be built and tested now --
swap ComingSoonScene out for the real scene class as each one lands.
"""

import pygame
from core.scene import Scene


class ComingSoonScene(Scene):
    def __init__(self, manager, app, game_name):
        super().__init__(manager)
        self.app = app
        self.game_name = game_name
        self.title_font = app.assets.get_font(None, 36)
        self.hint_font = app.assets.get_font(None, 20)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # local import avoids a circular import with menu_scene
                from scenes.menu_scene import build_menu_scene
                self.manager.switch_to(build_menu_scene(self.manager, self.app))

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((15, 15, 25))
        title = self.title_font.render(f"{self.game_name} - coming soon", True, (255, 255, 255))
        surface.blit(title, (40, 40))
        hint = self.hint_font.render("ESC = back to menu", True, (150, 150, 160))
        surface.blit(hint, (40, 90))