# calibre makes one of each Tool here when the editor starts. This one adds no action: it
# restyles the editor's windows and keeps the Lectrix syntax themes up to date, using the
# light or the dark one as calibre's mode changes.

from qt.core import QApplication

from calibre.gui2.tweak_book import editors, tprefs
from calibre.gui2.tweak_book.plugin import Tool

from .chrome import EDITOR_PREFS, current_mode, install, plugin_prefs, theme_enabled
from .lectrix_theme import EDITOR_THEME_NAMES, MODES, editor_theme

prefs = plugin_prefs(EDITOR_PREFS)
prefs.defaults['theme_chosen_once'] = False


def write_editor_themes():
    themes = tprefs['custom_themes']
    changed = False
    for mode in MODES:
        theme = editor_theme(mode)
        if themes.get(EDITOR_THEME_NAMES[mode]) != theme:
            themes[EDITOR_THEME_NAMES[mode]] = theme
            changed = True
    if changed:
        tprefs['custom_themes'] = themes


def choose_editor_theme():
    '''Use the Lectrix syntax theme for calibre's mode. Chosen once on the first start, and
    after that only swapped between light and dark while one of them is in use, so a theme
    picked in the editor's preferences stays. Returns whether the choice changed.'''
    current = tprefs['editor_theme']
    ours = set(EDITOR_THEME_NAMES.values())
    if not theme_enabled():
        if current in ours:
            wanted = None  # calibre's automatic choice
            prefs['theme_chosen_once'] = False  # chosen again when the theme is back on
        else:
            wanted = current
    elif not prefs['theme_chosen_once'] or current in ours:
        wanted = EDITOR_THEME_NAMES[current_mode(QApplication.instance())]
        prefs['theme_chosen_once'] = True
    else:
        wanted = current
    if wanted == current:
        return False
    tprefs['editor_theme'] = wanted
    return True


def apply_to_open_editors():
    for ed in editors.values():
        ed.apply_settings()
    try:
        from calibre.gui2.tweak_book.boss import get_boss

        get_boss().gui.live_css.apply_theme()
    except Exception:
        pass


class LectrixThemesTool(Tool):
    name = 'lectrix-themes'
    allowed_in_toolbar = False
    allowed_in_menu = False

    def __init__(self):
        install()
        try:
            write_editor_themes()
            choose_editor_theme()
        except Exception:
            import traceback

            traceback.print_exc()
        app = QApplication.instance()
        if app is not None and hasattr(app, 'palette_changed'):
            app.palette_changed.connect(self.on_palette_changed)

    def on_palette_changed(self):
        try:
            if choose_editor_theme():
                apply_to_open_editors()
        except Exception:
            import traceback

            traceback.print_exc()
