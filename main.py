"""Entry point. Right now this just proves App/Scene/SceneManager work
together (T1.4). Once R4 (menu) lands, this will start on MenuScene
instead of PlaceholderScene.
"""

import pygame
from core.app import App
from core.scene import Scene


class PlaceholderScene(Scene):
    def __init__(self, manager, app):
        super().__init__(manager)
        self.app = app
        self.font = app.assets.get_font(None, 36)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.app.running = False

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((20, 20, 30))
        text = self.font.render("Core engine running. ESC to quit.", True, (255, 255, 255))
        surface.blit(text, (40, 40))


if __name__ == "__main__":
    app = App(title="Salvage Arcade")
    app.run(PlaceholderScene(app.scenes, app))