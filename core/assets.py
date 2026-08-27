"""Shared asset cache (R3).

Loads each image/sound/font from disk once and hands out the cached
copy to whichever scene asks for it next, instead of every game
reloading its own duplicate assets like the original scripts do.

Also owns master_volume (R11): loaded from settings.json on startup,
applied to every newly-cached sound, and adjustable live via
set_master_volume().

KNOWN LIMITATION: a couple of GhostBusters' sound effects call their
own .set_volume() right after fetching them (e.g. diamond_fx is set to
0.6 for relative balance). Since that happens after AssetManager hands
the Sound object back, those specific effects will get blasted back to
the literal master_volume value if you change it while that scene is
active, rather than staying proportional to their authored 0.6 balance
-- they self-correct back to 0.6 the next time that scene is
constructed, since its __init__ re-applies the custom volume on top.
This is a known trade-off of keeping Settings to one simple slider
rather than a full per-effect mixing system.
"""

import os
import pygame

from core.settings_store import load_settings, save_settings


class AssetManager:
    def __init__(self, base_path="assets"):
        self.base_path = base_path
        self._images = {}
        self._sounds = {}
        self._fonts = {}
        self.master_volume = load_settings().get("master_volume", 1.0)

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
            sound = pygame.mixer.Sound(full_path)
            sound.set_volume(self.master_volume)
            self._sounds[relative_path] = sound
        return self._sounds[relative_path]

    def get_font(self, relative_path, size):
        """relative_path=None uses pygame's built-in default font."""
        key = (relative_path, size)
        if key not in self._fonts:
            full_path = os.path.join(self.base_path, relative_path) if relative_path else None
            self._fonts[key] = pygame.font.Font(full_path, size)
        return self._fonts[key]

    def set_master_volume(self, volume):
        """volume: 0.0-1.0. Applies immediately to every cached sound
        effect and to the music channel (if any track is loaded), and
        persists to settings.json."""
        self.master_volume = max(0.0, min(1.0, volume))
        for sound in self._sounds.values():
            sound.set_volume(self.master_volume)
        pygame.mixer.music.set_volume(self.master_volume)
        save_settings({"master_volume": self.master_volume})