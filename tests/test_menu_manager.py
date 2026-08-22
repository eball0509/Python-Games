"""Tests MenuScene's navigation/selection logic in isolation, using fake
App/AssetManager/SceneManager stand-ins instead of a real pygame window --
no display or audio driver needed to run these.
"""

import pygame
from scenes.menu_scene import MenuScene


class FakeFont:
    def render(self, *args, **kwargs):
        return None


class FakeAssets:
    def get_font(self, *args, **kwargs):
        return FakeFont()


class FakeApp:
    def __init__(self):
        self.assets = FakeAssets()
        self.running = True


class FakeManager:
    def __init__(self):
        self.switched_to = None

    def switch_to(self, scene):
        self.switched_to = scene


def key_event(key):
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def make_menu(entries=None):
    app = FakeApp()
    manager = FakeManager()
    if entries is None:
        entries = [
            ("A", "", lambda m, a: "scene_a"),
            ("B", "", lambda m, a: "scene_b"),
            ("C", "", lambda m, a: "scene_c"),
        ]
    return MenuScene(manager, app, entries), app, manager


def test_starts_on_first_entry():
    menu, _app, _manager = make_menu()
    assert menu.selected == 0


def test_down_advances_selection():
    menu, _app, _manager = make_menu()
    menu.handle_events([key_event(pygame.K_DOWN)])
    assert menu.selected == 1


def test_selection_wraps_past_the_end():
    menu, _app, _manager = make_menu()
    menu.handle_events([key_event(pygame.K_DOWN)] * 3)  # 3 entries -> wraps back to 0
    assert menu.selected == 0


def test_up_wraps_to_last_entry():
    menu, _app, _manager = make_menu()
    menu.handle_events([key_event(pygame.K_UP)])
    assert menu.selected == 2  # wraps to the last of 3 entries


def test_enter_switches_manager_to_the_selected_scene():
    menu, _app, manager = make_menu()
    menu.handle_events([key_event(pygame.K_DOWN)])  # selects "B"
    menu.handle_events([key_event(pygame.K_RETURN)])
    assert manager.switched_to == "scene_b"


def test_escape_sets_app_running_false():
    menu, app, _manager = make_menu()
    menu.handle_events([key_event(pygame.K_ESCAPE)])
    assert app.running is False