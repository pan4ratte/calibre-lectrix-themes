# Sets calibre's light and dark palettes (Look & feel > Adjust colors) to Lectrix's colors.
#
# Applied once, and again only when a plugin update changes the colors, so changes made in
# Adjust colors in between are kept. The palettes found before are backed up, and put back
# when the theme is turned off. Every calibre program (the viewer and the editor too) reads
# these same settings.

from .chrome import MAIN_PREFS, plugin_prefs
from .lectrix_theme import MODES, palette, palette_version

CURRENT = '__current__'  # the name calibre's Adjust colors saves its palettes under

prefs = plugin_prefs(MAIN_PREFS)
prefs.defaults['use_theme'] = True
prefs.defaults['applied_palette'] = None  # palette_version() last applied
prefs.defaults['palette_backup'] = None  # {mode: the palette from before}


def use_theme():
    return bool(prefs.get('use_theme', prefs.get('use_palette', True)))


def backups():
    saved = prefs['palette_backup'] or {}
    if 'name' in saved:  # from the version that set the dark palette only
        saved = {'dark': saved}
    return dict(saved)


def default_palette(mode):
    from calibre.gui2.palette import default_dark_palette, default_light_palette

    return default_dark_palette() if mode == 'dark' else default_light_palette()


def is_lectrix(pdata, mode):
    "Whether a saved palette is already Lectrix's, say imported from the palette file."
    if not pdata:
        return False
    from calibre.gui2.palette import palette_from_dict

    default = default_palette(mode)
    try:
        return palette_from_dict(pdata, default) == palette_from_dict(palette(mode), default)
    except Exception:
        return False


def apply_palettes():
    from calibre.gui2 import gprefs

    saved = backups()
    with gprefs:
        for mode in MODES:
            palettes = dict(gprefs[f'{mode}_palettes'])
            name = gprefs[f'{mode}_palette_name']
            if mode not in saved:
                current = palettes.get(CURRENT)
                if name and is_lectrix(current, mode):
                    # Lectrix's colors were imported by hand: turning off goes to calibre's own.
                    saved[mode] = {'name': '', 'current': None}
                else:
                    saved[mode] = {'name': name, 'current': current}
            palettes[CURRENT] = palette(mode)
            gprefs[f'{mode}_palettes'] = palettes
            gprefs[f'{mode}_palette_name'] = CURRENT
    prefs['palette_backup'] = saved
    prefs['applied_palette'] = palette_version()


def restore_palettes():
    from calibre.gui2 import gprefs

    saved = backups()
    with gprefs:
        for mode, backup in saved.items():
            palettes = dict(gprefs[f'{mode}_palettes'])
            if backup['current'] is None:
                palettes.pop(CURRENT, None)
            else:
                palettes[CURRENT] = backup['current']
            gprefs[f'{mode}_palettes'] = palettes
            gprefs[f'{mode}_palette_name'] = backup['name']
    prefs['palette_backup'] = None
    prefs['applied_palette'] = None


def sync_palette():
    'Apply or restore the palettes as the setting says. Returns whether anything changed.'
    if use_theme():
        if prefs['applied_palette'] == palette_version() and set(backups()) == set(MODES):
            return False
        apply_palettes()
    else:
        if not backups():
            return False
        restore_palettes()
    from calibre.gui2 import qapplication_or_fail

    manager = getattr(qapplication_or_fail(), 'palette_manager', None)
    if manager is not None:
        manager.refresh_palette()
    return True
