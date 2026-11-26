# The splash calibre shows while it starts, as a Lectrix card: rounded, in the mode's colors
# and font, with the calibre icon of the icon theme in use and a soft shadow.
#
# calibre loads its plugins before it starts the main window, so the plugin puts this splash
# in place of calibre's own before calibre shows it. Look & feel's Show splash screen setting
# turns it off as it does calibre's.

import sys

from qt.core import QApplication, QColor, QFont, QFontMetricsF, QIcon, QImage, QPainter, QPainterPath, QPen, QPixmap, QPointF, QRectF, QSize, QSplashScreen, Qt

from .chrome import FONT_FAMILY, current_mode, font_enabled, load_font, shadow_image
from .lectrix_theme import SPLASH_RADIUS, splash
from .palette import use_theme

# The layout, as a logo lockup is built: everything is measured from the icon's drawing, not
# its square, as icon themes leave blank space round their drawings, and from the capitals
# and baselines of text, not its line boxes.
#
# The icon stands on the name's baseline, so the two read as one line, and rises above the
# name's tallest letters to balance its weight. calibre's message is centred under them, and
# the theme's author under that, smaller. The card is square, with all of it centred in the
# card by its ink. That puts its weight a little above the middle, where the eye finds the
# middle, as the heavy name is at the top.
TITLE = 'Calibre'
TITLE_CAPS = 30  # px, the height of the name's capitals
ICON_SCALE = 1.3  # the icon's drawing, to the height of the name's tallest letters
ICON_GAP = 0.4  # from the icon's drawing to the name, to the height of those letters
TEXT_SIZE = 13  # px, calibre's message
MESSAGE_GAP = 20  # from the name's baseline to the message's capitals
CREDIT = 'Theme by Mark Ingrem'
CREDIT_SIZE = 11  # px
CREDIT_GAP = 12  # from the message's baseline to the author's capitals
PADDING = 48  # at least, above and below it all, and beside the message
SIDE_PADDING = 56  # at least, beside the icon and the name
MIN_SIZE = 360  # the card's side, made larger when the name or calibre's messages need it
# The icon's colors weigh more on the light card than the dark one: in light mode the icon and
# the name are left heavy by 3 px, in dark mode even. They go right by half of that.
OPTICAL_SHIFT = 1.5  # px


def interface_font(size, bold=False):
    font = QFont(QApplication.font())
    if font_enabled() and load_font(QApplication.instance()):
        font.setFamilies([FONT_FAMILY])
        font.setStyleStrategy(QFont.StyleStrategy.NoSubpixelAntialias)
        font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    font.setPixelSize(size)
    font.setBold(bold)
    return font


def font_with_caps(height, bold=False):
    "The interface font at the size whose capitals are this many pixels high."
    probe = interface_font(100, bold)
    caps = QFontMetricsF(probe).capHeight() or 70
    return interface_font(max(1, round(height * 100 / caps)), bold)


def drawing_box(icon, size=128):
    """Where an icon's drawing lies in its square, as fractions of the side: (left, top, right,
    bottom). The whole square when the icon is blank."""
    image = icon.pixmap(QSize(size, size)).toImage().convertToFormat(QImage.Format.Format_ARGB32)
    w, h = image.width(), image.height()
    if not w or not h:
        return 0.0, 0.0, 1.0, 1.0
    data = image.constBits().asstring(image.sizeInBytes())
    alpha = data[3::4]  # ARGB32 is stored as B, G, R, A
    rows = [y for y in range(h) if max(alpha[y * w:(y + 1) * w]) > 8]
    cols = [x for x in range(w) if max(alpha[x::w]) > 8]
    if not rows or not cols:
        return 0.0, 0.0, 1.0, 1.0
    return cols[0] / w, rows[0] / h, (cols[-1] + 1) / w, (rows[-1] + 1) / h


def round_up(value, step=8):
    return int(-(-value // step) * step)


class LectrixSplash(QSplashScreen):
    """Takes the place of calibre's SplashScreen: calibre calls show_message() and finish() on it.
    messages are the ones calibre will show, so the card is made wide enough for them in any
    language."""

    def __init__(self, mode, messages=()):
        self.drawn_once = False
        self.colors = splash(mode)
        self.icon = QIcon.ic('lt.png')  # calibre's icon, from the icon theme in use
        self.title_font = font_with_caps(TITLE_CAPS, bold=True)
        self.text_font = interface_font(TEXT_SIZE)
        self.credit_font = interface_font(CREDIT_SIZE)

        title = QFontMetricsF(self.title_font)
        self.name = title.tightBoundingRect(TITLE)  # the ink of the name, from its origin
        self.line_height = -self.name.top()  # from the baseline to the top of the tallest letters
        # The icon's square, sized so its drawing is ICON_SCALE times as high as those letters,
        # and the drawing in it.
        self.icon_height = ICON_SCALE * self.line_height
        left, top, right, bottom = drawing_box(self.icon)
        self.icon_size = self.icon_height / (bottom - top)
        self.drawing = QRectF(left * self.icon_size, top * self.icon_size, (right - left) * self.icon_size, self.icon_height)
        self.gap = ICON_GAP * self.line_height
        self.lockup_width = self.drawing.width() + self.gap + self.name.width()

        text, credit = QFontMetricsF(self.text_font), QFontMetricsF(self.credit_font)
        to_message = self.icon_height + MESSAGE_GAP + text.capHeight()  # from the icon's top to the message's baseline
        group = to_message + CREDIT_GAP + credit.capHeight()  # and to the author's
        widest = max((text.horizontalAdvance(m.strip()) for m in messages), default=0)
        size = max(MIN_SIZE, round_up(self.lockup_width + 2 * SIDE_PADDING), round_up(group + 2 * PADDING), round_up(widest + 2 * PADDING))
        self.card_width = self.card_height = size
        self.group_top = max(PADDING, (size - group) / 2)
        self.message_baseline = self.group_top + to_message
        self.credit_baseline = self.group_top + group

        dpr = QApplication.instance().devicePixelRatio()
        self.shadow, self.pad = shadow_image(self.card_width, self.card_height, self.colors['shadow'], dpr)
        w, h = self.card_width + 2 * self.pad, self.card_height + 2 * self.pad
        pmap = QPixmap(round(w * dpr), round(h * dpr))
        pmap.setDevicePixelRatio(dpr)
        pmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pmap)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle('calibre')

    def drawContents(self, painter):
        self.drawn_once = True
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        pad = self.pad
        painter.drawImage(QPointF(0, 0), self.shadow)
        card = QRectF(pad, pad, self.card_width, self.card_height)
        outline = QPainterPath()
        outline.addRoundedRect(card, SPLASH_RADIUS, SPLASH_RADIUS)
        painter.fillPath(outline, QColor(self.colors['card']))
        edge = QPainterPath()
        edge.addRoundedRect(card.adjusted(0.5, 0.5, -0.5, -0.5), SPLASH_RADIUS - 0.5, SPLASH_RADIUS - 0.5)
        painter.strokePath(edge, QPen(QColor(self.colors['edge']), 1))

        # The icon and the name, centred as one by their ink, the icon standing on the baseline.
        x = card.left() + (self.card_width - self.lockup_width) / 2 + OPTICAL_SHIFT
        top = card.top() + self.group_top
        baseline = top + self.icon_height
        size = self.icon_size
        square = QRectF(x - self.drawing.left(), top - self.drawing.top(), size, size)
        dpr = painter.device().devicePixelRatioF()
        pixmap = self.icon.pixmap(QSize(round(size), round(size)), dpr)
        painter.drawPixmap(square, pixmap, QRectF(pixmap.rect()))
        name_x = x + self.drawing.width() + self.gap - self.name.left()
        painter.setFont(self.title_font)
        painter.setPen(QColor(self.colors['title']))
        painter.drawText(QPointF(name_x, baseline), TITLE)

        # calibre's message under them, centred.
        message = (self.message() or '').strip()
        if message:
            text = QFontMetricsF(self.text_font)
            message = text.elidedText(message, Qt.TextElideMode.ElideRight, self.card_width - 2 * PADDING)
            ink = text.tightBoundingRect(message)
            mx = card.left() + (self.card_width - ink.width()) / 2 - ink.left()
            painter.setFont(self.text_font)
            painter.setPen(QColor(self.colors['text']))
            painter.drawText(QPointF(mx, card.top() + self.message_baseline), message)

        # The theme's author under it, centred.
        ink = QFontMetricsF(self.credit_font).tightBoundingRect(CREDIT)
        painter.setFont(self.credit_font)
        painter.setPen(QColor(self.colors['text']))
        cx = card.left() + (self.card_width - ink.width()) / 2 - ink.left()
        painter.drawText(QPointF(cx, card.top() + self.credit_baseline), CREDIT)
        painter.restore()

    def show_message(self, msg):
        self.drawn_once = False
        self.showMessage(msg)
        self.wait_for_draw()

    def wait_for_draw(self):
        """Let Windows show and paint the splash, as calibre's own does, since calibre is busy
        starting. Unlike calibre's, no wait when showMessage() painted it already."""
        from calibre.utils.monotonic import monotonic

        start = monotonic()
        while not self.drawn_once and monotonic() - start < 0.1:
            QApplication.processEvents()


def patch_splash():
    """Make calibre show the Lectrix splash in place of its own while the theme is on. Called as
    calibre loads the plugin, before its main window starts."""
    main = sys.modules.get('calibre.gui2.main')
    runner = getattr(main, 'GuiRunner', None)
    original = getattr(runner, 'show_splash_screen', None)
    if original is None or getattr(original, 'lectrix_themes', False):
        return

    def show_splash_screen(self):
        app = QApplication.instance()
        if app is None or not use_theme():
            return original(self)
        try:
            from calibre.constants import __appname__
            from calibre.utils.localization import _

            # calibre's two messages, the second shown by GuiRunner.start_gui()
            loading = _('Starting %s: Loading books...') % __appname__
            messages = (loading, _('Initializing user interface...'))
            self.splash_screen = LectrixSplash(current_mode(app), messages)
            self.splash_screen.show()
            self.splash_screen.show_message(loading)
        except Exception:
            import traceback

            traceback.print_exc()
            if self.splash_screen is not None:
                self.splash_screen.hide()
            original(self)

    show_splash_screen.lectrix_themes = True
    runner.show_splash_screen = show_splash_screen
