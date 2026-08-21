"""Single application shell (R1).

Owns the ONE pygame.init() call, the ONE window, and the ONE main loop
for the whole process. Every scene runs inside this loop instead of
each game having its own copy-pasted while-loop.
"""

import pygame


class App:
    def __init__(self, title="Salvage Arcade", size=(800, 600), fps=60, asset_path="assets"):
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.running = False

        # Imported here (not top-level) to avoid a circular import between
        # core.app / core.scene / core.assets during initial scaffolding.
        from core.scene import SceneManager
        from core.assets import AssetManager

        self.scenes = SceneManager()
        self.assets = AssetManager(asset_path)

    def run(self, first_scene):
        self.scenes.switch_to(first_scene)
        self.running = True

        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0  # seconds since last frame
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            active = self.scenes.active
            if active is None:
                self.running = False
                break

            active.handle_events(events)
            active.update(dt)
            active.draw(self.screen)
            pygame.display.flip()

        pygame.quit()