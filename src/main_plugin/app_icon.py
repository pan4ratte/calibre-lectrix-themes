# calibre's own icon, swapped for the calibre icon of the icon theme in use while the theme is
# on: on calibre's windows, its tray icon, and calibre's shortcuts on the taskbar, the desktop
# and the Start menu that Windows lets a user change.
#
# calibre gives the app its icon from its own files before it loads plugins, and the main
# window takes the app's icon when it is made, after. So the app's icon is swapped as the plugin
# loads (use_theme_icon()), and the main window and tray icon follow once they exist (refresh()).
#
# Windows draws a pinned taskbar button, and other shortcuts, with the shortcut's own icon, so
# those shortcuts are pointed at an .ico of the theme's icon, saved in calibre's settings
# folder. What each shortcut had is kept and put back when the theme is turned off. The Start
# menu shortcut calibre's installer makes is for all users, and only an administrator can
# change it, so it is left alone.

import os
import sys

from qt.core import QApplication, QBuffer, QByteArray, QIcon, QIODevice, QSize

from .palette import prefs, use_theme

ICON = 'lt.png'  # calibre's icon, as icon themes name it
ICO_SIZES = (16, 20, 24, 32, 40, 48, 64, 256)
prefs.defaults['shortcut_icons'] = {}  # {shortcut path: [icon path, icon index]} from before


def theme_icon():
    return QIcon.ic(ICON)


def use_theme_icon(app, enabled):
    "Give the app the theme's icon, or its own back. Windows and dialogs made after follow it."
    saved = getattr(app, 'lectrix_themes_window_icon', None)
    if enabled:
        if saved is None:
            app.lectrix_themes_window_icon = QIcon(app.windowIcon())
        app.setWindowIcon(theme_icon())
    elif saved is not None:
        app.lectrix_themes_window_icon = None
        app.setWindowIcon(saved)


def refresh(gui):
    "Follow the setting: the app's icon, the main window's, which it took when made, and the tray icon."
    app = QApplication.instance()
    enabled = use_theme()
    use_theme_icon(app, enabled)
    if gui is None:
        return
    gui.setWindowIcon(app.windowIcon())
    tray = getattr(gui, 'system_tray_icon', None)
    if tray is not None:
        saved = getattr(tray, 'lectrix_themes_icon', None)
        if enabled:
            if saved is None:
                tray.lectrix_themes_icon = QIcon(tray.icon())
            tray.setIcon(theme_icon())
        elif saved is not None:
            tray.lectrix_themes_icon = None
            tray.setIcon(saved)


# The shortcuts, on Windows only.


def ico_data(icon):
    "An .ico of an icon, with a PNG image at each of ICO_SIZES."
    import struct

    images = []
    for size in ICO_SIZES:
        image = icon.pixmap(QSize(size, size), 1.0).toImage()
        if image.isNull():
            continue
        data = QByteArray()
        buf = QBuffer(data)
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buf, 'PNG')
        buf.close()
        images.append((image.width(), image.height(), bytes(data)))
    header = struct.pack('<HHH', 0, 1, len(images))
    offset = len(header) + 16 * len(images)
    entries, body = b'', b''
    for w, h, png in images:
        entries += struct.pack('<BBBBHHII', w % 256, h % 256, 0, 0, 1, 32, len(png), offset + len(body))
        body += png
    return header + entries + body


def ico_path():
    from calibre.constants import config_dir

    return os.path.join(config_dir, 'plugins', 'lectrix_themes', 'calibre.ico')


def write_ico():
    "Write the theme's icon as an .ico, if it changed. Its path, and whether it changed."
    path = ico_path()
    data = ico_data(theme_icon())
    try:
        with open(path, 'rb') as f:
            if f.read() == data:
                return path, False
    except OSError:
        pass
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)
    return path, True


def folder(csidl):
    import ctypes

    buf = ctypes.create_unicode_buffer(260)
    if ctypes.windll.shell32.SHGetFolderPathW(None, csidl, None, 0, buf) != 0:
        return None
    return buf.value


CSIDL_APPDATA = 0x1A
CSIDL_DESKTOPDIRECTORY = 0x10


def shortcut_folders():
    "The folders of the user's own shortcuts: the pinned taskbar, the desktop and the Start menu."
    appdata = folder(CSIDL_APPDATA)
    ans = []
    if appdata:
        ans.append((os.path.join(appdata, 'Microsoft', 'Internet Explorer', 'Quick Launch', 'User Pinned', 'TaskBar'), False))
        ans.append((os.path.join(appdata, 'Microsoft', 'Windows', 'Start Menu', 'Programs'), True))
    desktop = folder(CSIDL_DESKTOPDIRECTORY)
    if desktop:
        ans.append((desktop, False))
    return ans


def calibre_shortcuts():
    "The user's shortcuts that start calibre."
    from .shell_link import ShellLink

    exe = os.path.normcase(os.path.join(os.path.dirname(sys.executable), 'calibre.exe'))
    for base, recursive in shortcut_folders():
        if not os.path.isdir(base):
            continue
        walk = os.walk(base) if recursive else [(base, (), os.listdir(base))]
        for dirpath, _, names in walk:
            for name in names:
                if not name.lower().endswith('.lnk'):
                    continue
                path = os.path.join(dirpath, name)
                try:
                    with ShellLink(path) as link:
                        target = link.target()
                except OSError:
                    continue
                if target and os.path.normcase(os.path.abspath(target)) == exe:
                    yield path


def update_shortcuts():
    "Point calibre's shortcuts at the theme's icon while the theme is on, and back when it's off."
    if sys.platform != 'win32':
        return
    from .shell_link import ShellLink, notify_changed

    saved = dict(prefs['shortcut_icons'])
    changed = []
    if use_theme():
        ico, ico_changed = write_ico()
        for path in calibre_shortcuts():
            with ShellLink(path) as link:
                current = link.icon_location()
                if os.path.normcase(current[0]) == os.path.normcase(ico):
                    if ico_changed:
                        changed.append(path)
                    continue
                saved[path] = list(current)  # what it had, or what was picked for it since
                link.set_icon_location(ico, 0)
                link.save()
            changed.append(path)
    else:
        ico = ico_path()
        for path, (icon, index) in saved.items():
            if not os.path.exists(path):
                continue
            with ShellLink(path) as link:
                if os.path.normcase(link.icon_location()[0]) != os.path.normcase(ico):
                    continue  # changed since: left as it is
                link.set_icon_location(icon, index)
                link.save()
            changed.append(path)
        saved = {}
    prefs['shortcut_icons'] = saved
    if changed:
        notify_changed(changed)
