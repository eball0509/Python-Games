"""Bullet and Grenade projectiles, ported from the original
GhostBusters/projectiles.py. Movement/collision/blast-radius math is
unchanged (see ADR-0002) -- including a very likely original bug in
Grenade.update() (see the comment there) that is being preserved
rather than "fixed," since ADR-0002 covers gameplay formulas, not just
the ones that look intentional.

The only real change: Grenade now takes an `assets` param so its blast
sound comes from the shared AssetManager instead of a module-level
pygame.mixer.Sound() loaded once at import time.
"""

import math
import pygame
from scenes.ghostbusters.particles import Explosion

WIDTH, HEIGHT = 640, 384


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, color, type_, win):
        super().__init__()

        self.x = x
        self.y = y
        self.direction = direction
        self.color = color
        self.type = type_
        self.win = win

        self.speed = 10
        self.radius = 4

        self.rect = pygame.draw.circle(self.win, self.color, (self.x, self.y), self.radius)

    def update(self, screen_scroll, world):
        if self.direction == -1:
            self.x -= self.speed + screen_scroll
        if self.direction == 0 or self.direction == 1:
            self.x += self.speed + screen_scroll

        for tile in world.ground_list:
            if tile[1].collidepoint(self.x, self.y):
                self.kill()
        for tile in world.rock_list:
            if tile[1].collidepoint(self.x, self.y):
                self.kill()

        self.rect = pygame.draw.circle(self.win, self.color, (self.x, self.y), self.radius)


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, win, assets):
        super().__init__()

        self.x = x
        self.y = y
        self.direction = direction
        self.win = win
        self.grenade_blast_fx = assets.get_sound("ghostbusters/grenade_blast.wav")
        self.grenade_blast_fx.set_volume(0.6)

        self.speed = 10
        self.vel_y = -11
        self.timer = 15
        self.radius = 4

        if self.direction == 0:
            self.direction = 1

        pygame.draw.circle(self.win, (200, 200, 200), (self.x, self.y), self.radius + 1)
        self.rect = pygame.draw.circle(self.win, (255, 50, 50), (self.x, self.y), self.radius)
        pygame.draw.circle(self.win, (0, 0, 0), (self.x, self.y), 1)

    def update(self, screen_scroll, p, enemy_group, explosion_group, world):
        self.vel_y += 1
        dx = self.direction * self.speed
        dy = self.vel_y

        for tile in world.ground_list:
            if tile[1].colliderect(self.rect.x, self.rect.y, self.rect.width, self.rect.height):
                if self.rect.y <= tile[1].y:
                    dy = 0
                    self.speed -= 1
                    if self.speed <= 0:
                        self.speed = 0

        for tile in world.rock_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                self.direction *= -1
                dx = self.direction * self.speed
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.rect.y <= tile[1].y:
                    dy = 0
                    self.speed -= 1
                    if self.speed <= 0:
                        self.speed = 0

        # NOTE: original compares to WIDTH here, not HEIGHT -- almost
        # certainly a bug (a grenade falling off the bottom of the level
        # should be checked against HEIGHT), but ADR-0002 says gameplay
        # formulas aren't touched during a port, bug-shaped or not.
        if self.rect.y > WIDTH:
            self.kill()

        if self.speed == 0:
            self.timer -= 1
            if self.timer <= 0:
                self.grenade_blast_fx.play()
                for _ in range(30):
                    explosion = Explosion(self.x, self.y, self.win)
                    explosion_group.add(explosion)

                p_distance = math.sqrt((p.rect.centerx - self.x) ** 2 + (p.rect.centery - self.y) ** 2)
                if p_distance <= 100:
                    if p_distance > 80:
                        p.health -= 20
                    elif p_distance > 40:
                        p.health -= 50
                    elif p_distance >= 0:
                        p.health -= 80
                    p.hit = True

                for e in enemy_group:
                    e_distance = math.sqrt((e.rect.centerx - self.x) ** 2 + (e.rect.centery - self.y) ** 2)
                    if e_distance < 80:
                        e.health -= 100

                self.kill()

        self.x += dx + screen_scroll
        self.y += dy

        pygame.draw.circle(self.win, (200, 200, 200), (self.x, self.y), self.radius + 1)
        self.rect = pygame.draw.circle(self.win, (255, 50, 50), (self.x, self.y), self.radius)
        pygame.draw.circle(self.win, (0, 0, 0), (self.x, self.y), 1)