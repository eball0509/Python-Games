"""Scene interface and SceneManager (R2).

Every game/menu screen implements Scene. SceneManager tracks which Scene
is active and switches between them. This is the piece that replaces the
hardcoded, one-file-per-game structure in the original repo.
"""

from abc import ABC, abstractmethod


class Scene(ABC):
    """Base class every game/menu screen must implement."""

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
        """Optional hook: called once when this scene becomes active."""
        pass

    def on_exit(self):
        """Optional hook: called once when this scene stops being active."""
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
            self._stack[-1].on_enter()

    def is_empty(self):
        return len(self._stack) == 0