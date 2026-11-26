from calibre.customize import InterfaceActionBase


class LectrixThemes(InterfaceActionBase):
    name = 'Lectrix themes'
    description = (
        "Lectrix's light and dark themes for calibre: its colors, and the title bar, fields,"
        " buttons, menus and tooltips the colors alone can't reach."
    )
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Mark'
    version = (1, 3, 0)
    minimum_calibre_version = (7, 0, 0)
    actual_plugin = 'calibre_plugins.lectrix_themes.action:LectrixThemesAction'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.lectrix_themes.config import ConfigWidget

        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()
        from calibre_plugins.lectrix_themes.chrome import restyle
        from calibre_plugins.lectrix_themes.palette import sync_palette

        sync_palette()
        restyle()
        from calibre_plugins.lectrix_themes.action import update_shortcuts_later

        update_shortcuts_later()


def install_startup():
    """Before the main window starts: put the Lectrix splash in place of calibre's (see
    splash.py), and give the app the theme's icon, which the main window takes (see app_icon.py)."""
    import sys

    if 'calibre.gui2.main' not in sys.modules:
        return  # not the main window: the viewer, the command-line programs and the rest
    try:
        from qt.core import QApplication

        from .app_icon import use_theme_icon
        from .palette import use_theme
        from .splash import patch_splash

        patch_splash()
        app = QApplication.instance()
        if app is not None and use_theme():
            use_theme_icon(app, True)
    except Exception:
        import traceback

        traceback.print_exc()


install_startup()
