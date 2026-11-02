# What the palette can't reach: the Windows title bar, fields, buttons, menus and tooltips,
# the Tag browser's hover, lists' current cell and the cards of Preferences. Styled for the mode calibre is in (light
# or dark), and all undone when the theme is turned off.

import sys

from qt.core import (
    QAbstractItemView,
    QAbstractScrollArea,
    QApplication,
    QColor,
    QEasingCurve,
    QEvent,
    QGraphicsEffect,
    QIcon,
    QImage,
    QLinearGradient,
    QMenu,
    QObject,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    QSize,
    Qt,
    QToolButton,
    QTransform,
    QVariantAnimation,
)

from .lectrix_theme import (
    CARD_EASE,
    CARD_LIFT,
    CARD_MARGIN,
    CARD_MOTION_MS,
    CARD_PRESSED_SCALE,
    CARD_RIPPLE,
    CARD_RIPPLE_DOT,
    CARD_RIPPLE_GROWTH,
    CARD_RIPPLE_MS,
    CARD_RIPPLE_OPACITY,
    CSS_EASE_OUT,
    MODES,
    arrow_images,
    card_edge,
    card_shadow,
    colorref,
    hover_text,
    pane_edge,
    popup_edge,
    shadow_extent,
    shadow_profile,
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
        refresh_preference_tiles(self.app)
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


# A Preferences card is this many pixels high, with the room round it: the icon, and up to
# two lines of text beside it.
PREFERENCE_CARD_HEIGHT = 70
PREFERENCE_ICON = 32  # calibre's icon size there
# Qt puts 4 px between a button's icon and its text: the icon gets this much blank space on
# its right for a wider gap.
PREFERENCE_ICON_GAP = 8
# What the text can't use of a card's width: its margin, edge and padding (as the stylesheet
# has them), the icon with its gap, and Qt's 4 px.
PREFERENCE_CARD_INSET = 2 * CARD_MARGIN + 2 + 24 + PREFERENCE_ICON + PREFERENCE_ICON_GAP + 4
QWIDGETSIZE_MAX = 16777215


def patch_preference_tiles(chrome):
    # calibre's Preferences shows its pages as flat buttons, a row to a category, each as wide
    # as a column of the window, with the name under the icon, and a line between categories.
    # With the theme on they are cards of one height with Lectrix's shadow, the name beside
    # the icon, so the rows line up as a grid of rectangles, and the lines go. The stylesheet
    # draws the cards, CardShadows their shadows.
    main = sys.modules.get('calibre.gui2.preferences.main')
    category = getattr(main, 'Category', None)
    original = getattr(category, 'update_button_widths', None)
    if original is None or getattr(original, 'lectrix_themes', False):
        return
    wrap = getattr(main, 'wrap_preference_button_text', None)
    separator = getattr(main, 'SectionSeparator', None)
    shadows = CardShadows(chrome, category)

    def update_button_widths(self, available_width=None):
        original(self, available_width)
        mode = chrome.mode
        shadows.watch(self)
        if separator is not None:
            for line in self.findChildren(separator):
                line.setVisible(mode is None)
        for button, text in getattr(self, 'buttons', ()):
            if mode is not None:
                button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
                button.setFixedHeight(PREFERENCE_CARD_HEIGHT)
                set_card_icon(button, True)
                set_card_lift(button, True, chrome)
                if wrap is not None:
                    width = button.minimumWidth() - PREFERENCE_CARD_INSET
                    button.setText(wrap(text, width, button.fontMetrics()))
            else:
                button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
                button.setMinimumHeight(0)
                button.setMaximumHeight(QWIDGETSIZE_MAX)
                set_card_icon(button, False)
                set_card_lift(button, False)

    update_button_widths.lectrix_themes = True
    category.update_button_widths = update_button_widths


def set_card_icon(button, card):
    "Give a Preferences button its icon with blank space on the right, or its own icon back."
    action = button.defaultAction()
    if action is None:
        return
    if not card:
        if getattr(button, 'lectrix_themes_icon', None) is not None:
            button.lectrix_themes_icon = None
            button.setIcon(action.icon())
            button.setIconSize(QSize(PREFERENCE_ICON, PREFERENCE_ICON))
        return
    dpr = button.devicePixelRatioF()
    if getattr(button, 'lectrix_themes_icon', None) == dpr:
        return
    size = PREFERENCE_ICON
    pixmap = QPixmap(round((size + PREFERENCE_ICON_GAP) * dpr), round(size * dpr))
    pixmap.setDevicePixelRatio(dpr)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    action.icon().paint(p, QRect(0, 0, size, size))
    p.end()
    button.setIcon(QIcon(pixmap))
    button.setIconSize(QSize(size + PREFERENCE_ICON_GAP, size))
    button.lectrix_themes_icon = dpr


def bezier(points):
    "A CSS cubic-bezier() as a Qt easing curve."
    curve = QEasingCurve(QEasingCurve.Type.BezierSpline)
    x1, y1, x2, y2 = points
    curve.addCubicBezierSegment(QPointF(x1, y1), QPointF(x2, y2), QPointF(1, 1))
    return curve


class CardMotion(QObject):
    """A Preferences card's motion, eased toward what the pointer asks for as Lectrix's
    transitions are: how far it is lifted, how far it has sunk on a press, how far its shadow
    and edge have gone from rest to hover, and the ripples of its presses."""

    def __init__(self, button, page):
        super().__init__(button)
        self.button, self.page = button, page
        self.hovered = False
        self.focused = False  # by the keyboard
        self.lift = 0.0  # px
        self.scale = 1.0
        self.raised = 0.0  # 0 the resting shadow and edge, 1 the hover ones
        self.ripples = []  # [x, y, progress from 0 to 1], in the button
        self.animations = {name: self.animation(name) for name in ('lift', 'scale', 'raised')}
        button.pressed.connect(self.retarget)
        button.released.connect(self.retarget)

    def animation(self, name):
        a = QVariantAnimation(self)
        a.setDuration(CARD_MOTION_MS)
        a.setEasingCurve(bezier(CARD_EASE))
        a.valueChanged.connect(lambda value: self.moved(name, value))
        return a

    def moved(self, name, value):
        setattr(self, name, float(value))
        self.repaint()

    def repaint(self):
        self.button.update()
        pos = self.button.mapTo(self.page, QPoint(0, 0))
        reach = 48  # past the button, for the hover shadow
        self.page.update(QRect(pos, self.button.size()).adjusted(-reach, -reach, reach, reach))

    @property
    def moving(self):
        return any(a.state() == QVariantAnimation.State.Running for a in self.animations.values())

    def retarget(self):
        down = self.button.isDown()
        lit = self.hovered or self.focused  # Lectrix: :hover or :focus-visible
        state = 'pressed' if down else 'hover' if lit else 'rest'
        targets = {
            'lift': float(CARD_LIFT[state]),
            'scale': CARD_PRESSED_SCALE if down else 1.0,
            'raised': 1.0 if state != 'rest' else 0.0,
        }
        for name, target in targets.items():
            a = self.animations[name]
            current = getattr(self, name)
            if a.state() == QVariantAnimation.State.Running and a.endValue() == target:
                continue
            a.stop()
            if current != target:
                a.setStartValue(current)
                a.setEndValue(target)
                a.start()

    def ripple(self, x, y):
        "Send a ripple out from where the card was pressed."
        ripple = [x, y, 0.0]
        self.ripples.append(ripple)
        a = QVariantAnimation(self)
        a.setDuration(CARD_RIPPLE_MS)
        a.setEasingCurve(bezier(CSS_EASE_OUT))
        a.setStartValue(0.0)
        a.setEndValue(1.0)

        def step(value):
            ripple[2] = float(value)
            self.button.update()

        def done():
            if ripple in self.ripples:
                self.ripples.remove(ripple)
            self.button.update()
            a.deleteLater()

        a.valueChanged.connect(step)
        a.finished.connect(done)
        a.start()


class CardLift(QGraphicsEffect):
    """Draws a Preferences card as its CardMotion has it: lifted and sunk, smoothly while it
    moves and on whole pixels at rest so the text is sharp, with its ripples and its edge."""

    def __init__(self, button, chrome):
        super().__init__(button)
        self.chrome = chrome

    def draw(self, painter):
        button = self.parent()
        motion = getattr(button, 'lectrix_themes_motion', None)
        mode = self.chrome.mode
        if motion is None or mode is None:
            self.drawSource(painter)
            return
        card = QRectF(button.rect()).adjusted(CARD_MARGIN, CARD_MARGIN, -CARD_MARGIN, -CARD_MARGIN)
        lift, scale = motion.lift, motion.scale
        dpr = button.devicePixelRatioF()
        if not motion.moving:
            lift = round(lift * dpr) / dpr
        # The card is drawn from its image, never with drawSource(): after that the painter
        # can't be used for the edge. No save() and restore() either, as Qt paints the card
        # through this same painter: what is changed is put back by hand.
        world = QTransform(painter.worldTransform())  # a copy: Qt gives the painter's own
        hints = painter.renderHints()
        c = card.center()
        move = QTransform()
        move.translate(c.x(), c.y() - lift)
        move.scale(scale, scale)
        move.translate(-c.x(), -c.y())
        pixmap, offset = self.sourcePixmap(Qt.CoordinateSystem.DeviceCoordinates, QGraphicsEffect.PixmapPadMode.NoPad)
        if not pixmap.isNull():
            inverse, ok = world.inverted()
            painter.setWorldTransform(inverse * move * world if ok else QTransform())
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, motion.moving or scale != 1)
            painter.drawPixmap(QPointF(offset), pixmap)
        painter.setWorldTransform(move * world)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        outline = QPainterPath()
        outline.addRoundedRect(card, 12, 12)
        r, g, b, a = CARD_RIPPLE
        for x, y, t in motion.ripples:
            radius = CARD_RIPPLE_DOT / 2 * CARD_RIPPLE_GROWTH * t
            dot = QPainterPath()
            dot.addEllipse(QPointF(x, y), radius, radius)
            opacity = a * CARD_RIPPLE_OPACITY * (1 - t)
            painter.fillPath(dot.intersected(outline), QColor(r, g, b, round(255 * opacity)))
        pen = QPen(QColor(card_edge(mode, motion.raised)))
        pen.setWidthF(1)
        edge = QPainterPath()
        edge.addRoundedRect(card.adjusted(0.5, 0.5, -0.5, -0.5), 11.5, 11.5)
        painter.strokePath(edge, pen)
        painter.setWorldTransform(world)
        painter.setRenderHints(hints)


def set_card_lift(button, card, chrome=None):
    "Give a Preferences button the effect that moves and edges it, or take it away."
    effect = button.graphicsEffect()
    if card:
        if effect is None:
            button.setGraphicsEffect(CardLift(button, chrome))
    elif isinstance(effect, CardLift):
        button.setGraphicsEffect(None)


def shadow_image(width, height, shadow, dpr):
    """A CSS box-shadow of a width x height box, as an image reaching shadow_extent() past the
    box on each side. A blurred box is its blur across times its blur down, so a gradient
    across, cut by a gradient down, draws it."""
    x, y, blur, spread, (r, g, b, a) = shadow
    pad = shadow_extent(shadow)
    w, h = width + 2 * pad, height + 2 * pad
    image = QImage(max(1, round(w * dpr)), max(1, round(h * dpr)), QImage.Format.Format_ARGB32_Premultiplied)
    image.setDevicePixelRatio(dpr)
    image.fill(Qt.GlobalColor.transparent)
    sigma = blur / 2
    across = QLinearGradient(0, 0, w, 0)
    for t, v in shadow_profile(w, pad + x - spread, pad + x + width + spread, sigma, max(16, w // 3)):
        across.setColorAt(t, QColor(r, g, b, round(255 * a * v)))
    down = QLinearGradient(0, 0, 0, h)
    for t, v in shadow_profile(h, pad + y - spread, pad + y + height + spread, sigma, max(16, h // 3)):
        down.setColorAt(t, QColor(0, 0, 0, round(255 * v)))
    p = QPainter(image)
    p.fillRect(QRectF(0, 0, w, h), across)
    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
    p.fillRect(QRectF(0, 0, w, h), down)
    p.end()
    return image, pad


class CardShadows(QObject):
    """Paints the shadows of the Preferences cards on the page behind them, where nothing
    between the cards clips them, and starts a card's motion as it is hovered."""

    def __init__(self, chrome, category):
        super().__init__(chrome)
        self.chrome = chrome
        self.category = category
        self.images = {}

    def watch(self, category):
        page = category.parentWidget()
        if page is None or isinstance(page, QAbstractScrollArea):
            return  # not in the page yet: calibre puts it there after making it
        if not getattr(page, 'lectrix_themes_shadows', False):
            page.lectrix_themes_shadows = True
            page.installEventFilter(self)
        for button, _ in getattr(category, 'buttons', ()):
            if getattr(button, 'lectrix_themes_motion', None) is None:
                button.lectrix_themes_motion = CardMotion(button, page)
                button.installEventFilter(self)
        page.update()

    def eventFilter(self, obj, event):
        t = event.type()
        if t == QEvent.Type.Paint and getattr(obj, 'lectrix_themes_shadows', False):
            mode = self.chrome.mode
            if mode is not None:
                try:
                    self.paint(obj, mode)
                except Exception:
                    import traceback

                    traceback.print_exc()
        elif isinstance(obj, QToolButton):
            motion = getattr(obj, 'lectrix_themes_motion', None)
            if motion is None or self.chrome.mode is None:
                return False
            if t in (QEvent.Type.Enter, QEvent.Type.Leave):
                motion.hovered = t == QEvent.Type.Enter
                motion.retarget()
            elif t in (QEvent.Type.FocusIn, QEvent.Type.FocusOut):
                # Lit only when Tab brought the focus, as :focus-visible is, not when the window
                # opened with the focus on it.
                keyboard = event.reason() in (Qt.FocusReason.TabFocusReason, Qt.FocusReason.BacktabFocusReason)
                motion.focused = t == QEvent.Type.FocusIn and keyboard
                motion.retarget()
            elif t == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                pos = event.position()
                motion.ripple(pos.x(), pos.y())
            elif t == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
                c = QRectF(obj.rect()).center()
                motion.ripple(c.x(), c.y())
        return False

    def paint(self, page, mode):
        dpr = page.devicePixelRatioF()
        p = QPainter(page)
        for category in page.findChildren(self.category):
            for button, _ in getattr(category, 'buttons', ()):
                if not button.isVisible():
                    continue
                w = button.width() - 2 * CARD_MARGIN
                h = button.height() - 2 * CARD_MARGIN
                if w <= 0 or h <= 0:
                    continue
                motion = getattr(button, 'lectrix_themes_motion', None)
                lift = motion.lift if motion is not None else 0
                raised = motion.raised if motion is not None else 0
                shadow = card_shadow(mode, raised)
                if raised in (0, 1):  # kept: the two shadows a card rests at
                    key = (w, h, shadow, dpr)
                    if key not in self.images:
                        if len(self.images) > 64:
                            self.images.clear()
                        self.images[key] = shadow_image(w, h, shadow, dpr)
                    image, pad = self.images[key]
                else:
                    image, pad = shadow_image(w, h, shadow, dpr)
                pos = button.mapTo(page, QPoint(0, 0))
                top = pos.y() + CARD_MARGIN - lift
                p.drawImage(QPointF(pos.x() + CARD_MARGIN - pad, top - pad), image)
        p.end()


def refresh_preference_tiles(app):
    "Resize an open Preferences' buttons when the theme is turned on or off."
    category = getattr(sys.modules.get('calibre.gui2.preferences.main'), 'Category', None)
    if category is None:
        return
    for top in app.topLevelWidgets():
        for widget in top.findChildren(category):
            try:
                widget.update_button_widths()
            except Exception:
                pass


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
    patch_preference_tiles(chrome)
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
