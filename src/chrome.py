# What the palette can't reach: the Windows title bar, fields, buttons, menus and tooltips,
# the Tag browser's hover and lists' current cell. Styled for the mode calibre is in (light
# or dark), and all undone when the theme is turned off.

import sys

from qt.core import QAbstractItemView, QApplication, QColor, QEvent, QMenu, QObject, QPainter, QRect, Qt

from .lectrix_theme import (
    MODES,
    arrow_images,
    colorref,
    hover_text,
    pane_edge,
    popup_edge,
    stylesheet,
    title_bar,
    tree_hover_stylesheet,
)

SEPARATOR = '\n/* Lectrix themes */'


MAIN_PREFS = ('lectrix_themes', 'proper_dark')  # the settings' name, and the project's old one
EDITOR_PREFS = ('lectrix_themes_editor', 'proper_dark_editor')


def plugin_prefs(names):
    "A plugin's settings, carried over once from the name the project had before."
    import os

    from calibre.utils.config import JSONConfig

    name, old_name = names
    prefs = JSONConfig(f'plugins/{name}')
    if not os.path.exists(prefs.file_path):
        old = JSONConfig(f'plugins/{old_name}')
        if os.path.exists(old.file_path):
            with prefs:
                for key, value in old.items():
                    prefs[key] = value
    return prefs


def theme_enabled():
    'The main plugin\'s "Use the Lectrix theme" setting, read afresh: the editor runs as its own program.'
    prefs = plugin_prefs(MAIN_PREFS)
    return bool(prefs.get('use_theme', prefs.get('use_palette', True)))


def current_mode(app):
    return 'dark' if getattr(app, 'is_dark_theme', False) else 'light'


# Lists that set this property have their current cell drawn by calibre's style in the
# selection color lightened, with black text in dark mode. The property is set aside while
# the theme is on, so the current cell looks like the rest of the selected row.
HIGHLIGHT_CURRENT = 'highlight_current_item'
SAVED_HIGHLIGHT_CURRENT = 'lectrix_themes_highlight_current_item'


def update_current_item_highlight(view, enabled):
    if enabled:
        value = view.property(HIGHLIGHT_CURRENT)
        if value:
            view.setProperty(SAVED_HIGHLIGHT_CURRENT, value)
            view.setProperty(HIGHLIGHT_CURRENT, None)
            view.viewport().update()
    else:
        value = view.property(SAVED_HIGHLIGHT_CURRENT)
        if value is not None:
            view.setProperty(HIGHLIGHT_CURRENT, value)
            view.setProperty(SAVED_HIGHLIGHT_CURRENT, None)
            view.viewport().update()


def write_arrows(mode):
    "Write a mode's arrow images to calibre's cache folder, and give the stylesheet using them."
    import os

    from calibre.constants import cache_dir

    folder = os.path.join(cache_dir(), 'lectrix-themes')
    os.makedirs(folder, exist_ok=True)
    paths = {}
    for key, svg in arrow_images(mode).items():
        dest = os.path.join(folder, f'{mode}-{key}.svg')
        try:
            with open(dest, encoding='utf-8') as f:
                current = f.read()
        except OSError:
            current = None
        if current != svg:
            with open(dest, 'w', encoding='utf-8') as f:
                f.write(svg)
        paths[key] = dest.replace(os.sep, '/')
    return stylesheet(mode, paths.__getitem__)


# DwmSetWindowAttribute attributes (Windows 11; the colors are ignored on Windows 10).
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_BORDER_COLOR = 34
DWMWA_CAPTION_COLOR = 35
DWMWA_TEXT_COLOR = 36
DWMWA_COLOR_DEFAULT = 0xFFFFFFFF
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_DEFAULT = 0
DWMWCP_ROUND = 2  # 8 px, as Lectrix's menus


def _set_dwm(hwnd, attribute, value):
    import ctypes

    v = ctypes.c_uint(value)
    ctypes.windll.dwmapi.DwmSetWindowAttribute(ctypes.c_void_p(hwnd), attribute, ctypes.byref(v), ctypes.sizeof(v))


def style_title_bar(hwnd, mode, system_dark=False):
    'Color a title bar for a mode, or give it back to Windows when mode is None.'
    if mode is None:
        _set_dwm(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, int(system_dark))
        for attribute in (DWMWA_CAPTION_COLOR, DWMWA_TEXT_COLOR, DWMWA_BORDER_COLOR):
            _set_dwm(hwnd, attribute, DWMWA_COLOR_DEFAULT)
        return
    colors = title_bar(mode)
    # The caption buttons follow this: light ones in dark mode, dark ones in light.
    _set_dwm(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, int(mode == 'dark'))
    _set_dwm(hwnd, DWMWA_CAPTION_COLOR, colorref(colors['caption']))
    _set_dwm(hwnd, DWMWA_TEXT_COLOR, colorref(colors['text']))
    _set_dwm(hwnd, DWMWA_BORDER_COLOR, colorref(colors['border']))


def style_popup(hwnd, mode):
    'Round a menu or dropdown list, with an edge of its color, or give it back to Windows.'
    if mode is None:
        _set_dwm(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, DWMWCP_DEFAULT)
        _set_dwm(hwnd, DWMWA_BORDER_COLOR, DWMWA_COLOR_DEFAULT)
        return
    _set_dwm(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, DWMWCP_ROUND)
    _set_dwm(hwnd, DWMWA_BORDER_COLOR, colorref(popup_edge(mode)['border']))


def is_rounded_popup(widget):
    "A menu or a dropdown's list: the popups Lectrix draws with round corners."
    if not widget.isWindow() or widget.windowType() != Qt.WindowType.Popup:
        return False
    return isinstance(widget, QMenu) or widget.metaObject().className() == 'QComboBoxPrivateContainer'


class Chrome(QObject):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.enabled = theme_enabled()
        self.styled = {}  # hwnd: the mode its title bar has, or None when given back
        self.stylesheets = {mode: write_arrows(mode) for mode in MODES}
        app.palette_changed.connect(self.refresh)
        app.focusWindowChanged.connect(self.on_focus_window)
        app.focusChanged.connect(self.on_focus_widget)
        if sys.platform == 'win32':
            app.installEventFilter(self)  # popups are rounded as they show

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Show and obj.isWidgetType() and is_rounded_popup(obj):
            try:
                style_popup(int(obj.winId()), self.mode)
            except Exception:
                pass
        return False

    @property
    def mode(self):
        'The mode to style for, or None while the theme is off.'
        return current_mode(self.app) if self.enabled else None

    def refresh(self):
        self.enabled = theme_enabled()
        mode = self.mode
        self.update_stylesheet(mode)
        for window in self.app.topLevelWindows():
            if window.isVisible():
                self.update_title_bar(window, mode)
        for top in self.app.topLevelWidgets():
            views = top.findChildren(QAbstractItemView)
            if isinstance(top, QAbstractItemView):
                views.append(top)
            for view in views:
                update_current_item_highlight(view, self.enabled)

    def update_stylesheet(self, mode):
        # calibre sets its stylesheet afresh on every palette change, then emits
        # palette_changed: ours goes on the end of it.
        ss = self.app.styleSheet()
        base = ss.partition(SEPARATOR)[0]
        wanted = base + SEPARATOR + self.stylesheets[mode] if mode else base
        if wanted != ss:
            self.app.setStyleSheet(wanted)

    def on_focus_window(self, window):
        # A window gets focus as it opens: style its title bar then.
        if window is not None:
            self.update_title_bar(window, self.mode)

    def on_focus_widget(self, old, new):
        # The current cell is only highlighted while its list has focus.
        if isinstance(new, QAbstractItemView):
            update_current_item_highlight(new, self.enabled)

    def update_title_bar(self, window, mode):
        if sys.platform != 'win32':
            return
        try:
            hwnd = int(window.winId())
        except Exception:
            return
        if not hwnd:
            return
        if hwnd in self.styled and self.styled[hwnd] == mode:
            return
        if mode is None and hwnd not in self.styled:
            return  # never changed it: nothing to give back
        try:
            hints = self.app.styleHints()
            system_dark = hints is not None and hints.colorScheme() == Qt.ColorScheme.Dark
            style_title_bar(hwnd, mode, system_dark)
        except Exception:
            return
        self.styled[hwnd] = mode


def patch_tree_hover(chrome):
    # calibre's hover in tree views is the selection color lightened: in dark mode brighter
    # than the selection itself, with the Tag browser's text in black on it. Lectrix's hover
    # is a faint tint.
    try:
        from calibre.gui2.palette import PaletteManager
    except Exception:
        return False
    original = PaletteManager.tree_view_hover_style
    if getattr(original, 'lectrix_themes', False):
        return True

    def tree_view_hover_style(self):
        mode = chrome.mode
        return tree_hover_stylesheet(mode) if mode else original(self)

    tree_view_hover_style.lectrix_themes = True
    PaletteManager.tree_view_hover_style = tree_view_hover_style

    # Only where the Tag browser is loaded already (calibre's main window).
    view = sys.modules.get('calibre.gui2.tag_browser.view')
    delegate = getattr(view, 'TagDelegate', None)
    if delegate is not None and hasattr(delegate, 'text_color'):
        original_color = delegate.text_color

        def text_color(self, hover, palette):
            mode = chrome.mode
            if hover and mode:
                return QColor(hover_text(mode))
            return original_color(self, hover, palette)

        delegate.text_color = text_color
    return True


def edge_side(handle):
    "The side of a panel's handle that faces the book list: 'left', 'right', 'top' or 'bottom'."
    book_list = getattr(handle.parent(), 'book_list', None)
    if book_list is None:
        return None
    h, b = handle.geometry(), book_list.geometry()
    if handle.orientation is Qt.Orientation.Vertical:  # a handle between columns
        if b.left() > h.right():
            return 'right'
        return 'left' if b.right() < h.left() else None
    if b.top() > h.bottom():
        return 'bottom'
    return 'top' if b.bottom() < h.top() else None


def edge_rect(rect, side, width):
    if side == 'left':
        return QRect(rect.left(), rect.top(), width, rect.height())
    if side == 'right':
        return QRect(rect.right() - width + 1, rect.top(), width, rect.height())
    if side == 'top':
        return QRect(rect.left(), rect.top(), rect.width(), width)
    return QRect(rect.left(), rect.bottom() - width + 1, rect.width(), width)


def patch_panel_edges(chrome):
    # The handles between the main window's panels and the book list are drawn by calibre's
    # style as a bar with dots. Lectrix's side panes end in a thin line instead, which takes
    # the accent while the pointer is on it.
    central = sys.modules.get('calibre.gui2.central')
    handle_class = getattr(central, 'SplitterHandle', None)
    if handle_class is None:
        return
    original = handle_class.paintEvent
    if getattr(original, 'lectrix_themes', False):
        return

    def paintEvent(self, event):
        mode = chrome.mode
        collapsed = min(self.width(), self.height()) <= getattr(self, 'COLLAPSED_SIZE', 2)
        side = None if mode is None or collapsed else edge_side(self)
        if side is None:
            return original(self, event)
        if not self.testAttribute(Qt.WidgetAttribute.WA_Hover):
            self.setAttribute(Qt.WidgetAttribute.WA_Hover)  # repaint as the pointer comes and goes
        colors = pane_edge(mode)
        p = QPainter(self)
        r = self.rect()
        p.fillRect(r, QColor(colors['pane']))
        if self.underMouse() or self.drag_start is not None:
            p.fillRect(edge_rect(r, side, 2), QColor(colors['hover']))
        else:
            p.fillRect(edge_rect(r, side, 1), QColor(colors['line']))
        p.end()

    paintEvent.lectrix_themes = True
    handle_class.paintEvent = paintEvent


def install():
    app = QApplication.instance()
    if app is None or not hasattr(app, 'palette_changed'):
        return None
    existing = getattr(app, 'lectrix_themes_chrome', None)
    if existing is not None:
        return existing
    chrome = Chrome(app)
    app.lectrix_themes_chrome = chrome
    patch_panel_edges(chrome)
    if patch_tree_hover(chrome):
        # Views that use the hover style restyle themselves on this signal.
        app.palette_changed.emit()
    else:
        chrome.refresh()
    return chrome


def restyle():
    'Apply a change of the setting at once: everything listening restyles on this signal.'
    app = QApplication.instance()
    if app is not None and hasattr(app, 'palette_changed'):
        app.palette_changed.emit()
