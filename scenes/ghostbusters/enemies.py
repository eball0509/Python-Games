"""Ghost enemy AI, ported from the original GhostBusters/enemies.py.
Patrol/shoot/death logic is unchanged (see ADR-0002). Images and the
enemy's gunshot sound now come from the shared, cached AssetManager
instead of a fresh pygame.image.load()/mixer.Sound() per instance.
"""

import random
import pygame
from scenes.ghostbusters.projectiles import Bullet

TILE_SIZE = 16


class Ghost(pygame.sprite.Sprite):
    def __init__(self, x, y, win, assets):
        super().__init__()

        self.x = x
        self.y = y
        self.win = win
        self.initial_pos_x = x

        self.size = 32
        self.bullet_fx = assets.get_sound("ghostbusters/ghost_shot.mp3")

        self.walk_left = []
        self.walk_right = []
        self.hit_list = []
        self.death_list = []

        for i in range(1, 6):
            image = assets.get_image(f"ghostbusters/Enemywalk{i}.png")
            right = pygame.transform.scale(image, (self.size, self.size))
            left = pygame.transform.flip(right, True, False)
            self.walk_right.append(right)
            self.walk_left.append(left)
        for i in range(1, 3):
            image = assets.get_image(f"ghostbusters/Enemyhit{i}.png")
            image = pygame.transform.scale(image, (self.size, self.size))
            self.hit_list.append(image)
        for i in range(1, 9):
            image = assets.get_image(f"ghostbusters/Enemydead{i}.png")
            image = pygame.transform.scale(image, (self.size, self.size))
            self.death_list.append(image)

        self.walk_index = 0
        self.death_index = 0
        self.hit_index = 0
        self.counter = 0

        self.dx = random.choice([-1, 1])
        self.alive = True
        self.health = 100
        self.hit = False
        self.on_death_bed = False

        self.image = self.walk_right[self.walk_index]
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, screen_scroll, bullet_group, p):
        if self.health:
            self.rect.x += (self.dx + screen_scroll)
            self.x += screen_scroll
            if abs(self.rect.x - self.x) >= 2 * TILE_SIZE:
                self.dx *= -1

        if self.health <= 0:
            self.on_death_bed = True

        self.counter += 1
        if self.counter % 5 == 0:
            if self.on_death_bed:
                self.death_index += 1
                if self.death_index >= len(self.death_list):
                    self.kill()
                    self.alive = False
            if self.hit:
                self.hit_index += 1
                if self.hit_index >= len(self.hit_list):
                    self.hit_index = 0
                    self.hit = False
            else:
                self.walk_index = (self.walk_index + 1) % len(self.walk_left)

        if self.counter % 50 == 0:
            if self.health > 0 and (abs(p.rect.x - self.rect.x) <= 200):
                x, y = self.rect.center
                direction = self.dx
                bullet = Bullet(x, y, direction, (160, 160, 160), 2, self.win)
                bullet_group.add(bullet)
                self.bullet_fx.play()

        if self.alive:
            if self.on_death_bed:
                self.image = self.death_list[self.death_index]
            elif self.hit:
                self.image = self.hit_list[self.hit_index]
            else:
                if self.dx == -1:
                    self.image = self.walk_left[self.walk_index]
                elif self.dx == 1:
                    self.image = self.walk_right[self.walk_index]

    def draw(self, win):
        win.blit(self.image, self.rect)