"""Scene interface and SceneManager (R2).

Every game/menu screen implements Scene. SceneManager tracks which Scene
is active and switches between them. This is the piece that replaces the
hardcoded, one-file-per-game structure in the original repo.
"""

from abc import ABC, abstractmethod


class Scene(ABC):
    """Base class every game/menu screen must implement."""

    # R8: whether pressing ESC on this scene should open the shared pause
    # overlay. MenuScene and PauseScene itself opt out (pausing the menu,
    # or pausing the pause screen, doesn't make sense).
    pauseable = True

    def __init__(self, manager):
        self.manager = manager  # lets a scene ask to switch to another scene

    @abstractmethod
    def handle_events(self, events):
        """events: the list of pygame.event.Event objects for this frame."""
        raise NotImplementedError

    @abstractmethod
    def update(self, dt):
        """dt: seconds elapsed since the last frame."""
        raise NotImplementedError

    @abstractmethod
    def draw(self, surface):
        """surface: the shared pygame.Surface to render onto."""
        raise NotImplementedError

    def on_enter(self):
        """Called once when this scene becomes active via switch_to() --
        i.e. a genuinely fresh start (selected from the menu). NOT
        called when resuming from a pause; see on_resume()."""
        pass

    def on_exit(self):
        """Called when this scene stops being the active scene, whether
        switch_to() replaced it or push() covered it with an overlay
        (e.g. the pause screen)."""
        pass

    def on_resume(self):
        """Called when this scene becomes active again after a scene
        that was pushed on top of it (e.g. the pause overlay) gets
        popped off. Kept separate from on_enter() so a scene can tell
        "starting fresh" apart from "continuing where you left off" --
        conflating the two was the cause of a real bug where resuming
        from pause reset games back to their start screen."""
        pass


class SceneManager:
    """Stack-based scene switcher. The top of the stack is the active scene.

    switch_to() replaces the whole stack (e.g. Menu -> Asteroids).
    push()/pop() layer a scene on top without losing what's underneath
    (e.g. opening the pause overlay on top of a running game) -- this is
    what R8's shared pause box is built on.
    """

    def __init__(self):
        self._stack = []

    @property
    def active(self):
        return self._stack[-1] if self._stack else None

    def switch_to(self, scene):
        if self._stack:
            self._stack[-1].on_exit()
        self._stack = [scene]
        scene.on_enter()

    def push(self, scene):
        if self._stack:
            self._stack[-1].on_exit()
        self._stack.append(scene)
        scene.on_enter()

    def pop(self):
        if not self._stack:
            return
        old = self._stack.pop()
        old.on_exit()
        if self._stack:
            self._stack[-1].on_resume()

    def is_empty(self):
        return len(self._stack) == 0