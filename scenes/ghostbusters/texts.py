"""Text, Message, BlinkingText, MessageBox -- ported from the original
GhostBusters/texts.py. Logic/positioning is unchanged from the original
(see ADR-0002). The one real change: font loading now goes through the
shared, cached AssetManager (R3) instead of a fresh pygame.font.Font()
call per instance -- same as Asteroids' font handling.
"""

import pygame


class Text:
    """Returns a rendered text image."""

    def __init__(self, font_path, font_size, assets):
        self.font = assets.get_font(font_path, font_size)

    def render(self, text, color):
        return self.font.render(text, False, color)


class Message:
    """Blits a rendered text image at a fixed position, with a drop shadow."""

    def __init__(self, x, y, size, text, font_path, color, win, assets):
        self.win = win
        self.color = color
        self.x, self.y = x, y

        if not font_path:
            # AssetManager.get_font(None, size) uses pygame's default font,
            # matching the original's pygame.font.SysFont("Verdana", size)
            # closely enough for a non-critical UI label; if the exact
            # Verdana look matters, swap this for a real font file instead.
            self.font = assets.get_font(None, size)
            anti_alias = True
        else:
            self.font = assets.get_font(font_path, size)
            anti_alias = False

        self.image = self.font.render(text, anti_alias, color)
        self.rect = self.image.get_rect(center=(x, y))

        if self.color == (200, 200, 200):
            self.shadow_color = (255, 255, 255)
        else:
            self.shadow_color = (54, 69, 79)
        self.shadow = self.font.render(text, anti_alias, self.shadow_color)
        self.shadow_rect = self.image.get_rect(center=(x + 2, y + 2))

    def update(self, text=None, color=None, shadow=True):
        if text:
            if not color:
                color = self.color
            self.image = self.font.render(f"{text}", False, color)
            self.rect = self.image.get_rect(center=(self.x, self.y))
            self.shadow = self.font.render(f"{text}", False, self.shadow_color)
            self.shadow_rect = self.image.get_rect(center=(self.x + 2, self.y + 2))
        if shadow:
            self.win.blit(self.shadow, self.shadow_rect)
        self.win.blit(self.image, self.rect)


class BlinkingText(Message):
    def __init__(self, x, y, size, text, font_path, color, win, assets):
        super().__init__(x, y, size, text, font_path, color, win, assets)
        self.index = 0
        self.show = True

    def update(self):
        self.index += 1
        if self.index % 40 == 0:
            self.show = not self.show

        if self.show:
            self.win.blit(self.image, self.rect)


def MessageBox(win, font, name, text):
    """Unchanged from the original -- draws a wrapped text box. `font`
    here is a plain pygame.font.Font object (e.g. from pygame.font.SysFont),
    not routed through AssetManager, matching the original's use of a
    one-off system font for this specific box.
    """
    WIDTH = 640
    HEIGHT = 284
    x = 35
    y = 65
    pygame.draw.rect(win, (255, 255, 255), (25, 25, WIDTH - 40, HEIGHT - 84), border_radius=10)
    for word in text.split(" "):
        rendered = font.render(word, 0, (0, 0, 0))
        width = rendered.get_width()
        if x + width >= WIDTH:
            x = 35
            y += 25
        win.blit(rendered, (x, y))
        x += width + 5

    title = font.render(name, 0, (0, 0, 0))
    title_width = 120
    pygame.draw.rect(
        win, (255, 255, 255), (WIDTH // 2 - title_width // 2 + 10, 10, title_width, 30), border_radius=10
    )
    win.blit(title, (WIDTH // 2 - title.get_width() // 2 + 10, 10))