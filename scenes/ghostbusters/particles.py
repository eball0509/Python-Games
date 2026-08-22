"""Trail and Explosion particle effects, ported from the original
GhostBusters/particles.py verbatim -- see ADR-0002 (gameplay formulas
are not touched during a port).

These classes draw themselves directly with pygame.draw calls at
construction and in update() (rather than exposing a separate draw()
method), matching the original's style. `win` is the same shared
surface every frame in our architecture (App.screen), so passing that
in place of the original's global `win` preserves identical behavior.
"""

import random
import pygame


class Trail(pygame.sprite.Sprite):
    def __init__(self, pos, color, win):
        super().__init__()
        self.color = color
        self.win = win

        self.x, self.y = pos
        self.y += 10
        self.dx = random.randint(0, 20) / 10 - 1
        self.dy = -2
        self.size = random.randint(4, 7)

        self.rect = pygame.draw.circle(self.win, self.color, (self.x, self.y), self.size)

    def update(self):
        self.x -= self.dx
        self.y -= self.dy
        self.size -= 0.1

        if self.size <= 0:
            self.kill()

        self.rect = pygame.draw.circle(self.win, self.color, (self.x, self.y), self.size)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, win):
        super().__init__()
        self.x = x
        self.y = y
        self.win = win

        self.size = random.randint(4, 9)
        self.life = 40
        self.lifetime = 0

        self.x_vel = random.randrange(-4, 4)
        self.y_vel = random.randrange(-4, 4)

        self.color = 150

    def update(self, screen_scroll):
        self.size -= 0.2
        self.lifetime += 1
        self.color -= 2
        if self.lifetime <= self.life:
            self.x += self.x_vel + screen_scroll
            self.y += self.y_vel
            s = int(self.size)
            pygame.draw.rect(self.win, (self.color, self.color, self.color), (self.x, self.y, s, s))
        else:
            self.kill()