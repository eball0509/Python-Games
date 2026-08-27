"""GhostBustersScene (R6): ports the original GhostBusters/ghostbusters.py
script onto the shared Scene/App architecture, preserving the full
original feature set (main menu / about page / controls page / win
screen / grenades / enemies / multi-level progression) per the
"full port" scope decision.

Structural changes from the original:
  - one shared App owns pygame.init()/window/clock instead of this file
    owning them (R1)
  - the whole game renders onto a fixed 640x384 internal surface, which
    is then scaled up to fill whatever the shared window's actual size
    is. This keeps every collision/scroll formula in player.py,
    world.py, etc. completely untouched (ADR-0002) instead of
    rewriting them for a different resolution.
  - asset loading goes through the shared, cached AssetManager (R3)
  - ESC (and Q, matching the original) returns to the main menu instead
    of quitting the whole process -- same navigation change as Asteroids
  - update(dt) is intentionally a no-op. The original interleaves
    physics, collision, and rendering in one per-frame block, and
    several of its classes (Bullet, Grenade, Trail, Explosion) draw
    themselves as a side effect of their own update() call rather than
    through a separate draw() step. Splitting that into a clean
    update-then-draw split risks silently reordering operations that
    depend on each other (e.g. screen_scroll being read by several
    groups *before* it's recomputed for the next frame). To guarantee
    feature parity, the entire original per-frame block lives in
    draw(surface), unmodified in sequence.
  - Button click detection still happens inside draw(), matching the
    original's design where Button.draw() both renders AND polls the
    mouse for a click in the same call

"""

import os
import pygame

from core.scene import Scene
from core.components.parallax import ParallaxBackground
from scenes.ghostbusters.world import World, load_level
from scenes.ghostbusters.player import Player
from scenes.ghostbusters.particles import Trail
from scenes.ghostbusters.projectiles import Bullet, Grenade
from scenes.ghostbusters.button import Button
from scenes.ghostbusters.texts import Text, Message, MessageBox

INTERNAL_SIZE = (640, 384)
TILE_SIZE = 16
SCROLL_THRES = 200
MAX_LEVEL = 3


class GhostBustersScene(Scene):
    def __init__(self, manager, app):
        super().__init__(manager)
        self.app = app
        self.assets = app.assets
        self.internal = pygame.Surface(INTERNAL_SIZE)

        self._load_images()
        self._load_fonts_and_text()
        self._load_sounds()
        self._build_buttons()

        self.trail_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.grenade_group = pygame.sprite.Group()
        self.explosion_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.water_group = pygame.sprite.Group()
        self.diamond_group = pygame.sprite.Group()
        self.potion_group = pygame.sprite.Group()
        self.exit_group = pygame.sprite.Group()
        self.objects_group = [
            self.water_group, self.diamond_group, self.potion_group,
            self.enemy_group, self.exit_group,
        ]

        self.p_image = pygame.transform.scale(self.assets.get_image("ghostbusters/PlayerIdle1.png"), (32, 32))
        self.p_rect = self.p_image.get_rect(center=(470, 200))
        self.p_dy = 1
        self.p_ctr = 1

        self.level = 1
        self.level_length = 0
        self.screen_scroll = 0
        self.bg_scroll = 0
        self.dx = 0

        self.main_menu = True
        self.about_page = False
        self.controls_page = False
        self.game_start = False
        self.game_won = False

        self.moving_left = False
        self.moving_right = False
        self.p = None
        self.world = None

        self.music_started = False

    # ---------------------------------------------------------------- setup
    def _load_images(self):
        self.BG1 = pygame.transform.scale(self.assets.get_image("ghostbusters/BG1.png"), INTERNAL_SIZE)
        self.BG2 = pygame.transform.scale(self.assets.get_image("ghostbusters/BG2.png"), INTERNAL_SIZE)
        self.BG3 = pygame.transform.scale(self.assets.get_image("ghostbusters/BG3.png"), INTERNAL_SIZE)
        self.MOON = pygame.transform.scale(self.assets.get_image("ghostbusters/moon.png"), (300, 220))
        self.ButtonBG = self.assets.get_image("ghostbusters/ButtonBG.png")

        # Shared component (also used by SalvageRunScene, R7) -- same
        # 0.6/0.7/0.8 layer speeds as the original's inline scroll code.
        self.background = ParallaxBackground(
            [(self.BG1, 0.6), (self.BG2, 0.7), (self.BG3, 0.8)], INTERNAL_SIZE,
        )

    def _load_fonts_and_text(self):
        title_font = "ghostbusters/Aladin-Regular.ttf"
        instructions_font = "ghostbusters/BubblegumSans-Regular.ttf"
        w, h = INTERNAL_SIZE

        self.ghostbusters_title = Message(w // 2 + 50, h // 2 - 90, 90, "GhostBusters",
                                           title_font, (255, 255, 255), self.internal, self.assets)
        self.left_key = Message(w // 2 + 10, h // 2 - 90, 20, "Press left arrow key to go left",
                                 instructions_font, (255, 255, 255), self.internal, self.assets)
        self.right_key = Message(w // 2 + 10, h // 2 - 65, 20, "Press right arrow key to go right",
                                  instructions_font, (255, 255, 255), self.internal, self.assets)
        self.up_key = Message(w // 2 + 10, h // 2 - 45, 20, "Press up arrow key to jump",
                               instructions_font, (255, 255, 255), self.internal, self.assets)
        self.space_key = Message(w // 2 + 10, h // 2 - 25, 20, "Press space key to shoot",
                                  instructions_font, (255, 255, 255), self.internal, self.assets)
        self.g_key = Message(w // 2 + 10, h // 2 - 5, 20, "Press g key to throw grenade",
                              instructions_font, (255, 255, 255), self.internal, self.assets)
        self.game_won_msg = Message(w // 2 + 10, h // 2 - 5, 20, "You have won the game",
                                     instructions_font, (255, 255, 255), self.internal, self.assets)

        t = Text(instructions_font, 18, self.assets)
        font_color = (12, 12, 12)
        self.play_label = t.render("Play", font_color)
        self.about_label = t.render("About", font_color)
        self.controls_label = t.render("Controls", font_color)
        self.exit_label = t.render("Exit", font_color)
        self.main_menu_label = t.render("Main Menu", font_color)

        self.about_font = pygame.font.SysFont("Times New Roman", 20)
        about_path = os.path.join(self.assets.base_path, "ghostbusters/about.txt")
        with open(about_path) as f:
            self.info = f.read().replace("\n", " ")

    def _load_sounds(self):
        self.diamond_fx = self.assets.get_sound("ghostbusters/point.mp3")
        self.diamond_fx.set_volume(0.6)
        self.bullet_fx = self.assets.get_sound("ghostbusters/bullet.wav")
        self.jump_fx = self.assets.get_sound("ghostbusters/jump.mp3")
        self.health_fx = self.assets.get_sound("ghostbusters/health.wav")
        self.menu_click_fx = self.assets.get_sound("ghostbusters/menu.mp3")
        self.next_level_fx = self.assets.get_sound("ghostbusters/level.mp3")
        # renamed from the original "grenade throw.wav" -- spaces in
        # asset filenames are asking for trouble on some platforms/tools
        self.grenade_throw_fx = self.assets.get_sound("ghostbusters/grenade_throw.wav")
        self.grenade_throw_fx.set_volume(0.6)

    def _build_buttons(self):
        bwidth = self.ButtonBG.get_width()
        cx, cy = INTERNAL_SIZE[0] // 2, INTERNAL_SIZE[1] // 2
        self.play_btn = Button(cx - bwidth // 4, cy, self.ButtonBG, 0.5, self.play_label, 10)
        self.about_btn = Button(cx - bwidth // 4, cy + 35, self.ButtonBG, 0.5, self.about_label, 10)
        self.controls_btn = Button(cx - bwidth // 4, cy + 70, self.ButtonBG, 0.5, self.controls_label, 10)
        self.exit_btn = Button(cx - bwidth // 4, cy + 105, self.ButtonBG, 0.5, self.exit_label, 10)
        self.main_menu_btn = Button(cx - bwidth // 4, cy + 130, self.ButtonBG, 0.5, self.main_menu_label, 20)

    # ------------------------------------------------------------- lifecycle
    def on_enter(self):
        if not self.music_started:
            music_path = os.path.join(self.assets.base_path, "ghostbusters/mixkit-complex-desire-1093.mp3")
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(loops=-1)
            pygame.mixer.music.set_volume(self.assets.master_volume)
            self.music_started = True

    def on_exit(self):
        # pygame.mixer.music is a single global channel shared by the
        # whole app -- without this, this scene's track keeps looping
        # forever even after switching to a different scene.
        pygame.mixer.music.stop()

    def _reset_level(self, level):
        self.trail_group.empty()
        self.bullet_group.empty()
        self.grenade_group.empty()
        self.explosion_group.empty()
        self.enemy_group.empty()
        self.water_group.empty()
        self.diamond_group.empty()
        self.potion_group.empty()
        self.exit_group.empty()

        data, level_length = load_level(level, self.assets)
        world = World(self.objects_group, self.assets)
        world.generate_world(data, self.internal)

        self.level_length = level_length
        self.world = world

    def _reset_player(self):
        self.p = Player(250, 50, self.assets)
        self.moving_left = False
        self.moving_right = False

    # --------------------------------------------------------------- events
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # ESC is no longer handled here -- App intercepts it
                # centrally and pushes the shared pause overlay (R8,
                # core/pause_scene.py) before this scene ever sees the
                # event. Q previously acted as an ESC alternate to match
                # the original's "ESC or Q quits" behavior; removed for
                # consistency now that neither Asteroids nor Salvage Run
                # has a Q shortcut, and Q now means "Quit" specifically
                # within the pause overlay itself.

                if event.key == pygame.K_LEFT:
                    self.moving_left = True
                if event.key == pygame.K_RIGHT:
                    self.moving_right = True
                if event.key == pygame.K_UP:
                    # original assumes self.p already exists here; guarded
                    # to avoid a crash if pressed before Play is ever
                    # clicked (self.p is None until _reset_player() runs)
                    if self.p is not None and not self.p.jump:
                        self.p.jump = True
                        self.jump_fx.play()
                if event.key == pygame.K_SPACE:
                    if self.p is not None:
                        x, y = self.p.rect.center
                        direction = self.p.direction
                        bullet = Bullet(x, y, direction, (240, 240, 240), 1, self.internal)
                        self.bullet_group.add(bullet)
                        self.bullet_fx.play()
                        self.p.attack = True
                if event.key == pygame.K_g:
                    if self.p is not None and self.p.grenades:
                        self.p.grenades -= 1
                        grenade = Grenade(self.p.rect.centerx, self.p.rect.centery, self.p.direction,
                                          self.internal, self.assets)
                        self.grenade_group.add(grenade)
                        self.grenade_throw_fx.play()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.moving_left = False
                if event.key == pygame.K_RIGHT:
                    self.moving_right = False

    # ------------------------------------------------------------- update
    def update(self, dt):
        # Intentional no-op -- see the module docstring. Everything the
        # original ran once per frame lives in draw() instead, in the
        # exact order the original script ran it in.
        pass

    # ---------------------------------------------------------------- draw
    def draw(self, surface):
        self._mouse_pos = self._internal_mouse_pos(surface)

        self.internal.fill((0, 0, 0))
        self.background.draw(self.internal)

        if not self.game_start:
            self.internal.blit(self.MOON, (-40, 150))

        if self.main_menu:
            self._do_main_menu()
        elif self.about_page:
            self._do_about_page()
        elif self.controls_page:
            self._do_controls_page()
        elif self.game_won:
            self._do_game_won()
        elif self.game_start:
            self._do_gameplay()

        pygame.draw.rect(self.internal, (255, 255, 255), (0, 0, *INTERNAL_SIZE), 4, border_radius=10)

        scaled = pygame.transform.scale(self.internal, surface.get_size())
        surface.blit(scaled, (0, 0))

    def _internal_mouse_pos(self, surface):
        """Real window clicks land in the window's own coordinate space,
        but every Button lives in the fixed 640x384 internal space (see
        the module docstring). Without this translation, clicks register
        against the wrong buttons whenever the shared window isn't
        exactly 640x384 -- which it never is."""
        real_x, real_y = pygame.mouse.get_pos()
        win_w, win_h = surface.get_size()
        scale_x = INTERNAL_SIZE[0] / win_w if win_w else 1
        scale_y = INTERNAL_SIZE[1] / win_h if win_h else 1
        return (real_x * scale_x, real_y * scale_y)

    # ---------------------------------------------------------- menu states
    def _do_main_menu(self):
        self.ghostbusters_title.update()
        self.trail_group.update()
        self.internal.blit(self.p_image, self.p_rect)
        self.p_rect.y += self.p_dy
        self.p_ctr += self.p_dy
        if self.p_ctr > 15 or self.p_ctr < -15:
            self.p_dy *= -1
        t = Trail(self.p_rect.center, (220, 220, 220), self.internal)
        self.trail_group.add(t)

        if self.play_btn.draw(self.internal, self._mouse_pos):
            self.menu_click_fx.play()
            self._reset_level(self.level)
            self._reset_player()
            self.game_start = True
            self.main_menu = False
            self.game_won = False

        if self.about_btn.draw(self.internal, self._mouse_pos):
            self.menu_click_fx.play()
            self.about_page = True
            self.main_menu = False

        if self.controls_btn.draw(self.internal, self._mouse_pos):
            self.menu_click_fx.play()
            self.controls_page = True
            self.main_menu = False

        if self.exit_btn.draw(self.internal, self._mouse_pos):
            self.menu_click_fx.play()
            from scenes.menu_scene import build_menu_scene
            self.manager.switch_to(build_menu_scene(self.manager, self.app))

    def _do_about_page(self):
        MessageBox(self.internal, self.about_font, "GhostBusters", self.info)
        if self.main_menu_btn.draw(self.internal, self._mouse_pos):
            self.menu_click_fx.play()
            self.about_page = False
            self.main_menu = True

    def _do_controls_page(self):
        self.left_key.update()
        self.right_key.update()
        self.up_key.update()
        self.space_key.update()
        self.g_key.update()

        if self.main_menu_btn.draw(self.internal, self._mouse_pos):
            self.menu_click_fx.play()
            self.controls_page = False
            self.main_menu = True

    def _do_game_won(self):
        self.game_won_msg.update()
        if self.main_menu_btn.draw(self.internal, self._mouse_pos):
            self.menu_click_fx.play()
            self.game_won = False
            self.main_menu = True
            self.level = 1

    # -------------------------------------------------------------- gameplay
    def _do_gameplay(self):
        self.internal.blit(self.MOON, (-40, -10))
        self.world.draw_world(self.internal, self.screen_scroll)

        # These all use `screen_scroll` as computed at the END of the
        # PREVIOUS frame (see the recompute further down) -- preserved in
        # this exact order to match the original script.
        self.bullet_group.update(self.screen_scroll, self.world)
        self.grenade_group.update(self.screen_scroll, self.p, self.enemy_group, self.explosion_group, self.world)
        self.explosion_group.update(self.screen_scroll)
        self.trail_group.update()
        self.water_group.update(self.screen_scroll)
        self.water_group.draw(self.internal)
        self.diamond_group.update(self.screen_scroll)
        self.diamond_group.draw(self.internal)
        self.potion_group.update(self.screen_scroll)
        self.potion_group.draw(self.internal)
        self.exit_group.update(self.screen_scroll)
        self.exit_group.draw(self.internal)

        self.enemy_group.update(self.screen_scroll, self.bullet_group, self.p)
        self.enemy_group.draw(self.internal)

        if self.p.jump:
            t = Trail(self.p.rect.center, (220, 220, 220), self.internal)
            self.trail_group.add(t)

        self.screen_scroll = 0
        self.p.update(self.moving_left, self.moving_right, self.world)
        self.p.draw(self.internal)

        if (self.p.rect.right >= INTERNAL_SIZE[0] - SCROLL_THRES
                and self.bg_scroll < (self.level_length * TILE_SIZE) - INTERNAL_SIZE[0]) \
                or (self.p.rect.left <= SCROLL_THRES and self.bg_scroll > abs(self.dx)):
            self.dx = self.p.dx
            self.p.rect.x -= self.dx
            self.screen_scroll = -self.dx
            self.bg_scroll -= self.screen_scroll
            # bg_scroll itself still drives the scroll-threshold math above
            # unchanged (ADR-0002); this just keeps the new shared
            # ParallaxBackground's render offset in sync with it.
            self.background.scroll_by(self.screen_scroll)

        # --------------------------------------------------- collisions
        if self.p.rect.bottom > INTERNAL_SIZE[1]:
            self.p.health = 0

        if pygame.sprite.spritecollide(self.p, self.water_group, False):
            self.p.health = 0
            self.level = 1

        if pygame.sprite.spritecollide(self.p, self.diamond_group, True):
            self.diamond_fx.play()

        if pygame.sprite.spritecollide(self.p, self.exit_group, False):
            self.next_level_fx.play()
            self.level += 1
            if self.level <= MAX_LEVEL:
                health = self.p.health
                self._reset_level(self.level)
                self._reset_player()
                self.p.health = health
                self.screen_scroll = 0
                self.bg_scroll = 0
                self.background.offset = 0.0
            else:
                self.game_won = True
                self.game_start = False

        potion_hit = pygame.sprite.spritecollide(self.p, self.potion_group, False)
        if potion_hit:
            if self.p.health < 100:
                potion_hit[0].kill()
                self.p.health += 15
                self.health_fx.play()
                if self.p.health > 100:
                    self.p.health = 100

        for bullet in list(self.bullet_group):
            enemy_hit = pygame.sprite.spritecollide(bullet, self.enemy_group, False)
            if enemy_hit and bullet.type == 1:
                if not enemy_hit[0].hit:
                    enemy_hit[0].hit = True
                    enemy_hit[0].health -= 50
                bullet.kill()
            if bullet.rect.colliderect(self.p.rect):
                if bullet.type == 2:
                    if not self.p.hit:
                        self.p.hit = True
                        self.p.health -= 20
                    bullet.kill()

        # --------------------------------------------------------- HUD
        if self.p.alive:
            color = (0, 255, 0)
            if self.p.health <= 40:
                color = (255, 0, 0)
            pygame.draw.rect(self.internal, color, (6, 8, self.p.health, 20), border_radius=10)
        pygame.draw.rect(self.internal, (255, 255, 255), (6, 8, 100, 20), 2, border_radius=10)

        for i in range(self.p.grenades):
            pygame.draw.circle(self.internal, (200, 200, 200), (20 + 15 * i, 40), 5)
            pygame.draw.circle(self.internal, (255, 50, 50), (20 + 15 * i, 40), 4)
            pygame.draw.circle(self.internal, (0, 0, 0), (20 + 15 * i, 40), 1)

        if self.p.health <= 0:
            self._reset_level(self.level)
            self._reset_player()
            self.screen_scroll = 0
            self.bg_scroll = 0
            self.background.offset = 0.0
            self.main_menu = True
            self.about_page = False
            self.controls_page = False
            self.game_start = False