"""World/tilemap loading and static level objects (Water, Diamond,
Potion, Exit, Ladder), ported from the original GhostBusters/world.py.
Tile-classification logic is unchanged (see ADR-0002). Changes:
  - tile images and level data now come from the shared AssetManager /
    assets/ghostbusters/ folder instead of loose Tiles/ and Levels/
    folders next to the script
  - World takes `assets` so it can pass it through to Ghost when
    spawning enemies during generate_world()
"""

import os
import pickle
import pygame

from scenes.ghostbusters.enemies import Ghost

NUM_TILES = 60
TILE_SIZE = 16


def load_tile_images(assets):
    return [assets.get_image(f"ghostbusters/{i}.png") for i in range(1, NUM_TILES + 1)]


class World:
    def __init__(self, objects_group, assets):
        self.objects_group = objects_group
        self.assets = assets
        self.img_list = load_tile_images(assets)

        self.ground_list = []
        self.rock_list = []
        self.decor_list = []

    def generate_world(self, data, win):
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = self.img_list[tile - 1]
                    rect = img.get_rect()
                    rect.x = x * TILE_SIZE
                    rect.y = y * TILE_SIZE
                    tile_data = (img, rect)

                    if tile in (0, 1, 2, 3, 4, 5, 6, 11):
                        self.ground_list.append(tile_data)

                    if tile in (7, 14, 18, 19, 20, 21, 25, 26, 27, 28, 32, 33, 34, 35, 42, 43, 44, 45):
                        self.rock_list.append(tile_data)

                    if tile in (8, 9, 10, 13, 15, 16, 17, 23, 24, 30, 31, 37, 38, 39, 40, 46, 47, 48, 49, 50, 51):
                        self.decor_list.append(tile_data)

                    if tile == 12:
                        exit_ = Exit(x * TILE_SIZE, y * TILE_SIZE, tile_data)
                        self.objects_group[4].add(exit_)

                    if tile == 41:
                        water = Water(x * TILE_SIZE, y * TILE_SIZE, tile_data)
                        self.objects_group[0].add(water)

                    if tile in (52, 53, 56, 57):
                        diamond = Diamond(x * TILE_SIZE, y * TILE_SIZE, tile_data)
                        self.objects_group[1].add(diamond)

                    if tile in (54, 55, 58, 59):
                        potion = Potion(x * TILE_SIZE, y * TILE_SIZE, tile_data)
                        self.objects_group[2].add(potion)

                    if tile == 60:
                        enemy = Ghost(x * TILE_SIZE, y * TILE_SIZE, win, self.assets)
                        self.objects_group[3].add(enemy)

    def draw_world(self, win, screen_scroll):
        for tile in self.ground_list:
            tile[1][0] += screen_scroll
            win.blit(tile[0], tile[1])
        for tile in self.rock_list:
            tile[1][0] += screen_scroll
            win.blit(tile[0], tile[1])
        for tile in self.decor_list:
            tile[1][0] += screen_scroll
            win.blit(tile[0], tile[1])


class Ladder(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_data):
        super().__init__()
        self.image = tile_data[0]
        self.rect = tile_data[1]
        self.rect.x = x
        self.rect.y = y

    def update(self, screen_scroll):
        self.rect.x += screen_scroll

    def draw(self, win):
        win.blit(self.image, self.rect)


class Water(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_data):
        super().__init__()
        self.image = tile_data[0]
        self.rect = tile_data[1]
        self.rect.x = x
        self.rect.y = y

    def update(self, screen_scroll):
        self.rect.x += screen_scroll

    def draw(self, win):
        win.blit(self.image, self.rect)


class Diamond(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_data):
        super().__init__()
        self.image = tile_data[0]
        self.rect = tile_data[1]
        self.rect.x = x
        self.rect.y = y

    def update(self, screen_scroll):
        self.rect.x += screen_scroll

    def draw(self, win):
        win.blit(self.image, self.rect)


class Potion(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_data):
        super().__init__()
        self.image = tile_data[0]
        self.rect = tile_data[1]
        self.rect.x = x
        self.rect.y = y

    def update(self, screen_scroll):
        self.rect.x += screen_scroll

    def draw(self, win):
        win.blit(self.image, self.rect)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_data):
        super().__init__()
        self.image = pygame.transform.scale(tile_data[0], (24, 24))
        self.rect = tile_data[1]
        self.rect.x = x
        self.rect.y = y - 8

    def update(self, screen_scroll):
        self.rect.x += screen_scroll

    def draw(self, win):
        win.blit(self.image, self.rect)


def load_level(level, assets):
    full_path = os.path.join(assets.base_path, f"ghostbusters/levels/level{level}_data")
    with open(full_path, "rb") as f:
        data = pickle.load(f)
        for y in range(len(data)):
            for x in range(len(data[0])):
                if data[y][x] >= 0:
                    data[y][x] += 1
    return data, len(data[0])