"""AsteroidsScene (R5): ports the original Asteroids/asteroids.py script
onto the shared Scene/App architecture. Gameplay behavior (movement,
timers, scoring, collision, silent reset-to-start-screen on death) is
preserved to match the original as closely as possible -- see ADR-0002.

Structural changes from the original script:
  - one shared App owns pygame.init()/window/clock instead of this file
    owning them
  - the original's global pygame.time.set_timer() asteroid spawn timers
    are replaced with per-scene delta-time accumulators (SPAWN_SCHEDULE
    below), since a global OS-level timer would keep firing into the
    event queue even while a different scene is active -- same spawn
    intervals (2s/6s/10s/15s/20s), different mechanism
  - asset loading goes through the shared, cached AssetManager instead
    of a raw pygame.image.load()/mixer.Sound() per object
  - ESC now returns to the main menu instead of quitting the whole
    process -- the previous behavior doesn't make sense once multiple
    games share one launcher (this is a navigation change, not a
    gameplay change, so it's outside ADR-0002's boundary)
"""

import os
import random
import pygame

from core.scene import Scene
from scenes.asteroids.objects import Rocket, Bullet, Asteroid, Explosion

# (spawn_interval_seconds, asteroid_type) -- matches the original's five
# ADDAST1..ADDAST5 timers (2s, 6s, 10s, 15s, 20s intervals)
SPAWN_SCHEDULE = [
    (2.0, 1),
    (6.0, 2),
    (10.0, 3),
    (15.0, 4),
    (20.0, 5),
]


class AsteroidsScene(Scene):
    def __init__(self, manager, app):
        super().__init__(manager)
        self.app = app
        self.assets = app.assets
        self.size = app.screen.get_size()

        self.font = self.assets.get_font(None, 32)
        self.gunshot_sound = self.assets.get_sound("asteroids/laser.wav")
        self.explosion_sound = self.assets.get_sound("asteroids/explosion.mp3")

        backgrounds = [f"asteroids/bg{i}s.png" for i in range(1, 5)]
        raw_bg = self.assets.get_image(random.choice(backgrounds), convert_alpha=False)
        raw_startbg = self.assets.get_image("asteroids/start.jpg", convert_alpha=False)
        # The original backgrounds were sized for a fixed 500x500 window.
        # R8 shares one window size across every scene, so scale the
        # background to fill whatever that size actually is, instead of
        # leaving stale pixels visible around the edges.
        self.bg = pygame.transform.scale(raw_bg, self.size)
        self.startbg = pygame.transform.scale(raw_startbg, self.size)

        self.started = False
        self.music_started = False
        self._reset_run()

    def _reset_run(self):
        self.score = 0
        self.rocket = Rocket(self.size, self.assets)
        self.asteroids = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.rocket)
        self.spawn_timers = [0.0 for _ in SPAWN_SCHEDULE]

    def on_exit(self):
        # pygame.mixer.music is a single global channel shared by the
        # whole app -- without this, this scene's track keeps looping
        # forever even after switching to a different scene.
        pygame.mixer.music.stop()

    def on_resume(self):
        # Pausing stops the music (on_exit above). Resuming must NOT
        # touch self.started -- that used to happen accidentally via
        # on_enter() (which also fires here before this fix), which is
        # exactly what caused resume to dump players back to the start
        # screen instead of continuing their run. Resetting only the
        # music flag makes the next update() naturally reload/replay
        # whichever track matches the current (untouched) self.started.
        self.music_started = False

    def handle_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            # ESC is no longer handled here -- App intercepts it centrally
            # and pushes the shared pause overlay (R8, core/pause_scene.py)
            # before this scene ever sees the event.

            if not self.started:
                if event.key == pygame.K_SPACE:
                    self.started = True
                    self.music_started = False
                continue

            if event.key == pygame.K_SPACE:
                pos = self.rocket.rect[:2]
                bullet = Bullet(pos, self.rocket.dir, self.size, self.assets)
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)
                self.gunshot_sound.play()
            elif event.key == pygame.K_q:
                self.rocket.rotate_left()
            elif event.key == pygame.K_e:
                self.rocket.rotate_right()

    def update(self, dt):
        if not self.started:
            self._ensure_music("asteroids/Apoxode_-_Electric_1.mp3")
            return

        self._ensure_music("asteroids/rpg_ambience_-_exploration.ogg")

        for i, (interval, asteroid_type) in enumerate(SPAWN_SCHEDULE):
            self.spawn_timers[i] += dt
            if self.spawn_timers[i] >= interval:
                self.spawn_timers[i] = 0.0
                ast = Asteroid(asteroid_type, self.size, self.assets)
                self.asteroids.add(ast)
                self.all_sprites.add(ast)

        pressed_keys = pygame.key.get_pressed()
        self.rocket.update(pressed_keys)
        self.asteroids.update()
        self.bullets.update()
        self.explosions.update()

        if pygame.sprite.spritecollideany(self.rocket, self.asteroids):
            self._reset_run()
            self.started = False
            self.music_started = False
            return

        for bullet in list(self.bullets):
            hit = pygame.sprite.spritecollide(bullet, self.asteroids, True)
            if hit:
                explosion = Explosion(bullet.rect[:2], self.assets)
                self.explosions.add(explosion)
                self.score += 1
                self.explosion_sound.play()
                bullet.kill()

    def _ensure_music(self, relative_path):
        if self.music_started:
            return
        full_path = os.path.join(self.assets.base_path, relative_path)
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.set_volume(self.assets.master_volume)
        self.music_started = True

    def draw(self, surface):
        if not self.started:
            surface.blit(self.startbg, (0, 0))
            return

        surface.blit(self.bg, (0, 0))
        self.explosions.draw(surface)
        for sprite in self.all_sprites:
            surface.blit(sprite.surf, sprite.rect)
        surface.blit(self.rocket.surf, self.rocket.rect)

        text = self.font.render(f"Score : {self.score}", True, (200, 255, 0))
        surface.blit(text, (surface.get_width() - 160, 10))