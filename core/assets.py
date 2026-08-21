"""Shared asset cache (R3).

Loads each image/sound/font from disk once and hands out the cached
copy to whichever scene asks for it next, instead of every game
reloading its own duplicate assets like the original scripts do.
"""

import os
import pygame


class AssetManager:
    def __init__(self, base_path="assets"):
        self.base_path = base_path
        self._images = {}
        self._sounds = {}
        self._fonts = {}

    def get_image(self, relative_path, convert_alpha=True):
        if relative_path not in self._images:
            full_path = os.path.join(self.base_path, relative_path)
            image = pygame.image.load(full_path)
            image = image.convert_alpha() if convert_alpha else image.convert()
            self._images[relative_path] = image
        return self._images[relative_path]

    def get_sound(self, relative_path):
        if relative_path not in self._sounds:
            full_path = os.path.join(self.base_path, relative_path)
            self._sounds[relative_path] = pygame.mixer.Sound(full_path)
        return self._sounds[relative_path]

    def get_font(self, relative_path, size):
        """relative_path=None uses pygame's built-in default font."""
        key = (relative_path, size)
        if key not in self._fonts:
            full_path = os.path.join(self.base_path, relative_path) if relative_path else None
            self._fonts[key] = pygame.font.Font(full_path, size)
        return self._fonts[key]