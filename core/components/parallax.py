"""ParallaxBackground: a reusable multi-layer scrolling background.

Extracted from the layered-scroll logic that used to live inline in
GhostBustersScene.draw() (BG1/BG2/BG3 blitted at 0.6/0.7/0.8 of the
scroll amount). This is the actual architectural deliverable R6/R7 were
about: proving that piece is reusable, not just that two games exist.

Two ways to drive it:
  - `scroll_by(amount)` -- GhostBusters' style: the background only
    moves when the game logic says so (player crossing a scroll
    threshold), driven by player position.
  - `auto_scroll(dt, speed)` -- Salvage Run's style: the background
    moves on its own every frame, independent of player input.

Both just adjust the same internal `self.offset`, so a scene can even
mix styles if it ever needs to.
"""


class ParallaxBackground:
    def __init__(self, layers, size):
        """layers: list of (image, speed_multiplier) tuples, back-to-front
        (e.g. [(BG1, 0.6), (BG2, 0.7), (BG3, 0.8)] -- lower multiplier
        scrolls slower, giving the illusion of being further away).
        size: (width, height) of one background tile -- used to figure
        out how many repeated copies are needed to fill the screen.
        """
        self.layers = layers
        self.width, self.height = size
        self.offset = 0.0

    def scroll_by(self, amount):
        self.offset -= amount

    def auto_scroll(self, dt, speed):
        """speed in pixels/second."""
        self.offset -= speed * dt

    def draw(self, surface, tiles_wide=5):
        surface_width = surface.get_width()
        for image, multiplier in self.layers:
            layer_offset = self.offset * multiplier
            # normalize into [-width, 0) so we never need more than
            # tiles_wide copies regardless of how large offset has grown
            layer_offset %= self.width
            start_x = -self.width + layer_offset
            x = start_x
            while x < surface_width:
                surface.blit(image, (x, 0))
                x += self.width