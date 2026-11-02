from calibre.gui2.actions import InterfaceAction

from .chrome import install, restyle
from .palette import prefs, sync_palette, use_theme

NAME = 'Lectrix themes'
# Where calibre keeps the buttons of each toolbar and menu bar.
BARS = ('toolbar', 'toolbar-device', 'toolbar-child', 'searchbar', 'menubar', 'menubar-device')
# calibre's Color palette choices in Adjust colors.
COLOR_PALETTES = (('light', 'Light'), ('dark', 'Dark'), ('system', 'System default'))


def add_button_once():
    """Put the button on the main toolbar, once, for those updating from a version without it.

    calibre asks where to put the button on a new install, but not on an update.
    """
    if prefs.get('button_added'):
        return
    # applied_palette is saved at the first start, so it's there only on an update.
    updating = 'applied_palette' in prefs
    prefs['button_added'] = True
    if not updating:
        return
    from calibre.gui2 import gprefs

    if any(NAME in gprefs[f'action-layout-{bar}'] for bar in BARS):
        return
    for bar in ('toolbar', 'toolbar-device'):
        gprefs[f'action-layout-{bar}'] = tuple(gprefs[f'action-layout-{bar}']) + (NAME,)


def set_color_palette(name):
    "Set calibre's Color palette, as Adjust colors does."
    from calibre.gui2 import gprefs
    from qt.core import QApplication

    gprefs['color_palette'] = name
    manager = getattr(QApplication.instance(), 'palette_manager', None)
    if manager is not None:
        manager.refresh_palette()


class LectrixThemesAction(InterfaceAction):
    name = NAME
    action_spec = (NAME, None, 'Switch between light and dark. Right-click for more.', None)
    # The button has nothing to do with books, so no book menus.
    dont_add_to = frozenset(('context-menu', 'context-menu-split', 'context-menu-device', 'context-menu-cover-browser'))

    def genesis(self):
        install()
        try:
            add_button_once()
        except Exception:
            import traceback

            traceback.print_exc()
        try:
            sync_palette()
        except Exception:
            import traceback

            traceback.print_exc()
        self.qaction.setIcon(get_icons('images/icon.png', NAME))  # noqa: F821, calibre provides get_icons
        self.qaction.triggered.connect(self.toggle_mode)
        self.build_menu()

    def build_menu(self):
        "The menu shown on right-click, or by the button's arrow."
        from qt.core import QActionGroup, QMenu

        self.menu = menu = QMenu(self.gui)
        group = QActionGroup(menu)
        self.palette_actions = {}
        for key, text in COLOR_PALETTES:
            ac = menu.addAction(text)
            ac.setCheckable(True)
            group.addAction(ac)
            ac.triggered.connect(lambda checked, key=key: set_color_palette(key))
            self.palette_actions[key] = ac
        menu.addSeparator()
        self.use_theme_action = ac = menu.addAction('Use the Lectrix theme')
        ac.setCheckable(True)
        ac.toggled.connect(self.set_use_theme)
        menu.aboutToShow.connect(self.update_menu)
        self.qaction.setMenu(menu)

    def update_menu(self):
        "Tick what is in use now: the settings can also change in Preferences."
        from calibre.gui2 import gprefs

        current = self.palette_actions.get(gprefs['color_palette'])
        if current is not None:
            current.setChecked(True)
        ac = self.use_theme_action
        ac.blockSignals(True)
        ac.setChecked(use_theme())
        ac.blockSignals(False)

    def toggle_mode(self):
        "Switch to dark if calibre shows light now, and to light if it shows dark."
        from qt.core import QApplication

        dark = getattr(QApplication.instance(), 'is_dark_theme', False)
        set_color_palette('light' if dark else 'dark')

    def set_use_theme(self, on):
        prefs['use_theme'] = bool(on)
        sync_palette()
        restyle()
