from core.scene import Scene, SceneManager


class DummyScene(Scene):
    """Minimal concrete Scene for testing SceneManager in isolation --
    no pygame window or event loop needed."""

    def __init__(self, manager, name):
        super().__init__(manager)
        self.name = name
        self.entered = False
        self.exited = False

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass

    def on_enter(self):
        self.entered = True

    def on_exit(self):
        self.exited = True


def test_switch_to_replaces_active_scene():
    manager = SceneManager()
    menu = DummyScene(manager, "menu")
    game = DummyScene(manager, "game")

    manager.switch_to(menu)
    assert manager.active is menu
    assert menu.entered

    manager.switch_to(game)
    assert manager.active is game
    assert menu.exited
    assert game.entered
    assert len(manager._stack) == 1  # switch_to discards, it doesn't stack


def test_push_and_pop_preserves_scene_beneath():
    manager = SceneManager()
    game = DummyScene(manager, "game")
    pause = DummyScene(manager, "pause")

    manager.switch_to(game)
    manager.push(pause)
    assert manager.active is pause
    assert game.exited  # game paused, not destroyed

    manager.pop()
    assert manager.active is game
    assert pause.exited


def test_empty_manager_has_no_active_scene():
    manager = SceneManager()
    assert manager.active is None
    assert manager.is_empty()