from calibre.customize import InterfaceActionBase


class LectrixThemes(InterfaceActionBase):
    name = 'Lectrix themes'
    description = (
        "Lectrix's light and dark themes for calibre: its colors, and the title bar, fields,"
        " buttons, menus and tooltips the colors alone can't reach."
    )
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Mark'
    version = (1, 2, 0)
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


def install_splash():
    "Put the Lectrix splash in place of calibre's, before the main window starts: see splash.py."
    import sys

    if 'calibre.gui2.main' not in sys.modules:
        return  # not the main window: the viewer, the command-line programs and the rest
    try:
        from .splash import patch_splash

        patch_splash()
    except Exception:
        import traceback

        traceback.print_exc()


install_splash()
