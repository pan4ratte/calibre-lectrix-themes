from calibre.gui2.actions import InterfaceAction

from .chrome import install
from .palette import sync_palette


class LectrixThemesAction(InterfaceAction):
    name = 'Lectrix themes'
    action_spec = ('Lectrix themes', None, None, None)
    # Nothing to click: the plugin only restyles the windows.
    dont_add_to = InterfaceAction.all_locations

    def genesis(self):
        install()
        try:
            sync_palette()
        except Exception:
            import traceback

            traceback.print_exc()
