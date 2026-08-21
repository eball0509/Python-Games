"""Entry point. Boots into the main menu (R4). Each menu entry currently
opens a ComingSoonScene stand-in -- swap those for AsteroidsScene,
GhostBustersScene, and SalvageRunScene as R5/R6/R7 get built.
"""

from core.app import App
from scenes.menu_scene import build_menu_scene

if __name__ == "__main__":
    app = App(title="Salvage Arcade")
    app.run(build_menu_scene(app.scenes, app))