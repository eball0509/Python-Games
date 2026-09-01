"""SalvageRunScene (R7): an original game built directly on the shared
architecture, proving the extracted pieces are genuinely reusable --
not just that two ported games happen to exist alongside each other.

Reuses:
  - core.components.parallax.ParallaxBackground (extracted from
    GhostBusters, R6), driven here with auto_scroll() instead of
    GhostBusters' player-position-driven scroll_by()
  - the same "clamp movement to screen bounds" concept as Asteroids'
    Rocket, written fresh in entities.Ship since Rocket carries
    Asteroids-specific rotation/facing logic that has no place here

Unlike the ported games, this one uses delta-time movement throughout
from the start -- there's no original script to preserve frame-counted
parity with, so it's written the way R1's architecture actually intends.
"""

import random
import pygame

from core.scene import Scene
from core.components.parallax import ParallaxBackground
from scenes.salvage_run.entities import Ship, Hazard, Salvage

BG_SCROLL_SPEED = 90    # pixels/second, auto-scroll -- not player-driven
SPAWN_INTERVAL = 1.2    # seconds between hazard/salvage spawns
SALVAGE_CHANCE = 0.4    # fraction of spawns that are salvage rather than hazards


class SalvageRunScene(Scene):
    def __init__(self, manager, app):
        super().__init__(manager)
        self.app = app
        self.assets = app.assets
        self.size = app.screen.get_size()

        self.title_font = self.assets.get_font(None, 44)
        self.hint_font = self.assets.get_font(None, 18)
        self.score_font = self.assets.get_font(None, 32)

        # Flat-color layers stand in for real art -- swap these for real
        # background images later the same way BG1/2/3 work in
        # GhostBusters; ParallaxBackground doesn't care what's on them.
        layer_far = pygame.Surface(self.size)
        layer_far.fill((10, 10, 35))
        layer_mid = pygame.Surface(self.size)
        layer_mid.fill((20, 20, 55))
        layer_near = pygame.Surface(self.size)
        layer_near.fill((30, 30, 75))
        self.background = ParallaxBackground(
            [(layer_far, 0.3), (layer_mid, 0.6), (layer_near, 1.0)], self.size,
        )

        self.started = False
        self._reset_run()

    def _reset_run(self):
        self.score = 0
        self.ship = Ship(self.size)
        self.hazards = pygame.sprite.Group()
        self.salvage = pygame.sprite.Group()
        self.spawn_timer = 0.0
        self.moving_up = self.moving_down = self.moving_left = self.moving_right = False

    # No on_enter()/on_resume() overrides needed: __init__ already sets
    # started=False for a fresh selection from the menu, and there's no
    # music here to restart after a pause the way the ported games need.
    # (An earlier on_enter() override that reset self.started here was
    # the actual bug -- SceneManager used to call on_enter() on resume
    # too, so resuming was silently kicking back to the start screen.)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # ESC is no longer handled here -- App intercepts it
                # centrally and pushes the shared pause overlay (R8,
                # core/pause_scene.py) before this scene ever sees it.

                if not self.started:
                    if event.key == pygame.K_SPACE:
                        self._reset_run()
                        self.started = True
                    continue

                if event.key in (pygame.K_UP, pygame.K_w):
                    self.moving_up = True
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.moving_down = True
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.moving_left = True
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.moving_right = True

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.moving_up = False
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.moving_down = False
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.moving_left = False
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.moving_right = False

    def update(self, dt):
        self.background.auto_scroll(dt, BG_SCROLL_SPEED)

        if not self.started:
            return

        self.ship.update(dt, self.moving_up, self.moving_down, self.moving_left, self.moving_right)
        self.hazards.update(dt)
        self.salvage.update(dt)

        self.spawn_timer += dt
        if self.spawn_timer >= SPAWN_INTERVAL:
            self.spawn_timer = 0.0
            if random.random() < SALVAGE_CHANCE:
                self.salvage.add(Salvage(self.size))
            else:
                self.hazards.add(Hazard(self.size))

        if pygame.sprite.spritecollideany(self.ship, self.hazards):
            self._reset_run()
            self.started = False
            return

        collected = pygame.sprite.spritecollide(self.ship, self.salvage, True)
        self.score += len(collected)

    def draw(self, surface):
        self.background.draw(surface)

        if not self.started:
            title = self.title_font.render("SALVAGE RUN", True, (255, 255, 255))
            surface.blit(title, (surface.get_width() // 2 - title.get_width() // 2, 120))
            hint = self.hint_font.render(
                "Arrows/WASD to move, dodge hazards, collect salvage -- SPACE to start",
                True, (200, 200, 210),
            )
            surface.blit(hint, (surface.get_width() // 2 - hint.get_width() // 2, 180))
            return

        self.hazards.draw(surface)
        self.salvage.draw(surface)
        surface.blit(self.ship.image, self.ship.rect)

        score_text = self.score_font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(score_text, (surface.get_width() - 160, 10))