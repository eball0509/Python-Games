"""Shared pause overlay (R8). App pushes this on top of whatever scene
is active when ESC is pressed (see App.run()), instead of every scene
implementing its own ESC behavior. Matches the original pause mockup:
ESC resumes, M returns to the main menu, Q quits.

Pushed via SceneManager.push() rather than switch_to(), so the paused
scene underneath is preserved (not destroyed/reset) and resumes exactly
where it was.

`snapshot` is a copy of the screen taken at the moment of pausing. It's
redrawn fresh every frame before the overlay tint is applied -- without
this, re-blending a semi-transparent tint onto an already-tinted
surface every frame would make the screen get darker and darker the
longer you stay paused.
"""

import pygame
from core.scene import Scene

BOX_SIZE = (360, 220)
BOX_FILL = (15, 23, 42, 235)
BORDER_COLOR = (148, 163, 184)


class PauseScene(Scene):
    pauseable = False  # you can't pause the pause screen

    def __init__(self, manager, app, snapshot):
        super().__init__(manager)
        self.app = app
        self.snapshot = snapshot
        self.title_font = app.assets.get_font(None, 30)
        self.option_font = app.assets.get_font(None, 22)

    def handle_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                self.manager.pop()
                return
            if event.key == pygame.K_m:
                from scenes.menu_scene import build_menu_scene
                self.manager.switch_to(build_menu_scene(self.manager, self.app))
                return
            if event.key == pygame.K_q:
                self.app.running = False
                return

    def update(self, dt):
        pass

    def draw(self, surface):
        # Restore the clean pre-pause frame first, every frame, so the
        # tint below never compounds.
        surface.blit(self.snapshot, (0, 0))

        tint = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        tint.fill((0, 0, 0, 120))
        surface.blit(tint, (0, 0))

        box_w, box_h = BOX_SIZE
        box_x = surface.get_width() // 2 - box_w // 2
        box_y = surface.get_height() // 2 - box_h // 2
        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill(BOX_FILL)
        pygame.draw.rect(box, BORDER_COLOR, box.get_rect(), width=2, border_radius=10)

        title = self.title_font.render("PAUSED", True, (255, 255, 255))
        box.blit(title, (box_w // 2 - title.get_width() // 2, 24))

        options = ["ESC   ->  Resume", "M     ->  Return to Menu", "Q     ->  Quit"]
        for i, text in enumerate(options):
            opt_surf = self.option_font.render(text, True, (203, 213, 225))
            box.blit(opt_surf, (40, 90 + i * 34))

        surface.blit(box, (box_x, box_y))