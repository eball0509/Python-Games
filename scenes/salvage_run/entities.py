"""Ship, Hazard, and Salvage sprites for Salvage Run (R7) -- an
original game, not a port. Movement is written with delta-time from
the start (all speeds are pixels/second) rather than preserving any
frame-counted behavior, since there's no original script to match.

Placeholder art: these draw simple vector shapes with pygame.draw
instead of loading image files, so the game is playable without
needing any new art assets created first. Swap in real sprites later
by loading images in place of the pygame.draw calls below -- nothing
else about these classes needs to change.
"""

import random
import pygame

SHIP_SPEED = 220       # pixels/second
HAZARD_SPEED = 160      # pixels/second
SALVAGE_SPEED = 140     # pixels/second


class Ship(pygame.sprite.Sprite):
    def __init__(self, bounds_size):
        super().__init__()
        self.bounds_width, self.bounds_height = bounds_size

        self.image = pygame.Surface((36, 24), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (250, 210, 60), [(0, 0), (0, 24), (36, 12)])
        self.rect = self.image.get_rect(center=(80, self.bounds_height // 2))

    def update(self, dt, moving_up, moving_down, moving_left, moving_right):
        dx = dy = 0.0
        if moving_up:
            dy -= SHIP_SPEED * dt
        if moving_down:
            dy += SHIP_SPEED * dt
        if moving_left:
            dx -= SHIP_SPEED * dt
        if moving_right:
            dx += SHIP_SPEED * dt

        self.rect.x += dx
        self.rect.y += dy

        # Clamp to bounds -- same concept as Asteroids' Rocket, written
        # fresh here since this is new code, not a port of it.
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(self.bounds_width, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(self.bounds_height, self.rect.bottom)


class Hazard(pygame.sprite.Sprite):
    def __init__(self, bounds_size):
        super().__init__()
        bounds_width, bounds_height = bounds_size
        radius = random.randint(12, 22)

        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 40, 40), (radius, radius), radius)
        pygame.draw.circle(self.image, (140, 20, 20), (radius, radius), radius, 3)
        self.rect = self.image.get_rect(
            center=(bounds_width + radius, random.randint(radius, max(radius, bounds_height - radius)))
        )

    def update(self, dt):
        self.rect.x -= HAZARD_SPEED * dt
        if self.rect.right < 0:
            self.kill()


class Salvage(pygame.sprite.Sprite):
    def __init__(self, bounds_size):
        super().__init__()
        bounds_width, bounds_height = bounds_size
        size = 16

        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.polygon(
            self.image, (190, 190, 195),
            [(size // 2, 0), (size, size // 2), (size // 2, size), (0, size // 2)],
        )
        self.rect = self.image.get_rect(
            center=(bounds_width + size, random.randint(size, max(size, bounds_height - size)))
        )

    def update(self, dt):
        self.rect.x -= SALVAGE_SPEED * dt
        if self.rect.right < 0:
            self.kill()