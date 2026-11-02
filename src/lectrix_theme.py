# Lectrix's light and dark themes for calibre: every color in one place.
#
# The values are Lectrix's design tokens (lectrix/src/app.css): Neo's light theme and its
# Midnight dark theme, tinted toward Lectrix blue, the Lectrix blue accent, and Neo's named
# colors. build.py writes the palette file from here, and both plugins carry a copy of this
# module. Everything below is given per mode: 'light' or 'dark'.

MODES = ('light', 'dark')

TOKENS = {
    'light': {
        'chrome': '#f2f4f7',  # title bar, toolbars and panes
        'surface': '#f9fafb',  # lists, fields, the editor
        'menu': '#e4e9f1',  # menus, tooltips
        'raised': '#f9fafb',  # cards
        'card_hover_line': '#6fa3ef',  # a card's edge under the pointer
        'button': '#f2f4f7',
        'button_hover': '#e4e9f1',
        'line': '#ccd3dd',
        'line_strong': '#bec5cf',
        'fg': '#22252a',
        'fg_muted': '#505762',
        'fg_strong': '#121417',  # headings and titles
        'accent': '#2f5daa',
        'accent_fg': '#ffffff',  # text on the accent
        'danger': '#c9303a',
        # Neo's named colors, deepened here to 4.5:1 on the surface for text in the editor.
        'blue': '#4c71c0',
        'pink': '#bf4385',
        'green': '#0a842f',
        'orange': '#b55719',
        'purple': '#6f55f1',
        'teal': '#207e87',
        'diff_inserted': '#136429',
        'diff_deleted': '#a61f1f',
    },
    'dark': {
        'chrome': '#131416',
        'surface': '#0c0d0e',
        'menu': '#1c1e22',
        'raised': '#1c1e22',
        'card_hover_line': '#6fa3ef',
        'button': '#262a31',
        'button_hover': '#2a2f37',
        'line': '#303540',
        'line_strong': '#3a404a',
        'fg': '#a9b0bc',
        'fg_muted': '#929baa',
        'fg_strong': '#e1e5ea',
        'accent': '#6fa3ef',
        'accent_fg': '#0f1a33',
        'danger': '#e85a5f',
        'blue': '#7ab0f7',
        'pink': '#ff97cf',
        'green': '#22d0a2',
        'orange': '#ed8b4f',
        'purple': '#9580ff',
        'teal': '#3eb4bf',
        'diff_inserted': '#4ac26b',
        'diff_deleted': '#f47067',
    },
}

# Blends that CSS works out with color-mix() or opacity, precomputed for Qt.
BLENDS = {
    'light': {
        'selected': '#d3dceb',  # --lectrix-row-selected (accent at 16%) on the chrome
        'hover_surface': '#e1e7f1',  # --lectrix-hover (rgb(77 116 179 / 0.14)) on each background
        'hover_menu': '#cfd9e8',
        'hover_chrome': '#dbe2ed',
        'disabled': '#94979b',  # the text at 45% opacity on the chrome
        'button_disabled': '#f2f4f7',  # the button at 45% opacity on the chrome
        'accent_hover': '#294e8d',  # --lectrix-accent-hover: 80% accent, toward the strong text
        'text_selection': '#b8c8e1',  # --lectrix-selection (accent at 32%) on the surface
        'emphasis': '#e4e9f1',  # a matching bracket, a non-breaking space in the editor
        'line_number': '#8a8c90',
        'comment': '#6d7073',
        'diff_deleted_bg': '#f6dedf',
        'diff_inserted_bg': '#d9ecde',
        'diff_replaced_bg': '#e1e7f1',
    },
    'dark': {
        'selected': '#222b39',
        'hover_surface': '#1d2024',
        'hover_menu': '#2b2f36',
        'hover_chrome': '#23262b',
        'disabled': '#565a61',
        'button_disabled': '#1c1e22',
        'accent_hover': '#86b0ee',
        'text_selection': '#2c3d56',
        'emphasis': '#2a2f37',
        'line_number': '#666a71',
        'comment': '#72777f',
        'diff_deleted_bg': '#311d1c',
        'diff_inserted_bg': '#162a1d',
        'diff_replaced_bg': '#1c2532',
    },
}


def palette(mode):
    "calibre's palette (Preferences > Look & feel > Adjust colors) for a mode."
    T, B = TOKENS[mode], BLENDS[mode]
    ans = {
        'Window': T['chrome'],
        'Base': T['surface'],
        'AlternateBase': T['chrome'],
        'Button': T['button'],
        'ToolTipBase': T['menu'],
        'Highlight': B['selected'],
        'Accent': T['accent'],
        'WindowText': T['fg'],
        'Text': T['fg'],
        'ButtonText': T['fg'],
        'ToolTipText': T['fg'],
        'PlaceholderText': T['fg_muted'],
        'HighlightedText': T['fg_strong'],
        'BrightText': T['fg_strong'],
        'Link': T['accent'],
        'LinkVisited': T['purple'],
    }
    for key in [k for k in ans if 'Text' in k]:
        ans[key + '-disabled'] = B['disabled']
    return ans


def palette_version():
    'Changes whenever a palette color does, so the plugin knows to apply the palettes again.'
    import hashlib
    import json

    data = json.dumps({mode: palette(mode) for mode in MODES}, sort_keys=True)
    return hashlib.sha1(data.encode('utf-8')).hexdigest()[:12]


def colorref(hex_color):
    'A #rrggbb color as a Windows COLORREF (0x00bbggrr).'
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return r | (g << 8) | (b << 16)


def popup_edge(mode):
    "The edge of menus and dropdown lists, which Windows 11 rounds as Lectrix's menus are."
    return {'border': TOKENS[mode]['line_strong']}


def title_bar(mode):
    'The Windows title bar, for every calibre window.'
    T = TOKENS[mode]
    return {'caption': T['chrome'], 'text': T['fg_strong'], 'border': T['line']}


def pane_edge(mode):
    '''The edge between a side panel and the book list, as Lectrix's side panes have: the
    panel's color up to a thin line, and the accent line of its resizer under the pointer.'''
    T = TOKENS[mode]
    return {'pane': T['chrome'], 'line': T['line'], 'hover': T['accent']}


# Scrollbars are WebView2's thin ones, as Lectrix shows them: no track, a thumb in the text
# color at 35% (70% under the pointer), and a small triangle at each end.
SCROLL_THUMB_ALPHA = 0.35
SCROLL_THUMB_HOVER_ALPHA = 0.7


def rgba(hex_color, alpha):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return f'rgba({r}, {g}, {b}, {alpha})'


# Arrows for dropdowns, number fields, sorted columns and scrollbars: Qt stylesheets need
# image files, which chrome.py writes to calibre's cache folder.
ARROWS = {
    'down': 'M3 6l5 5 5-5',
    'up': 'M3 10l5-5 5 5',
}
SCROLL_ARROWS = {
    'scroll-up': 'M0 5.25L3 0.75L6 5.25Z',
    'scroll-down': 'M0 0.75L3 5.25L6 0.75Z',
    'scroll-left': 'M5.25 0L0.75 3L5.25 6Z',
    'scroll-right': 'M0.75 0L5.25 3L0.75 6Z',
}


def arrow_images(mode):
    "Every arrow image of a mode, as {name: svg}, for names such as 'down' and 'up-disabled'."
    T, B = TOKENS[mode], BLENDS[mode]
    ans = {}
    for name, path in ARROWS.items():
        for suffix, color in (('', T['fg_muted']), ('-disabled', B['disabled'])):
            ans[name + suffix] = (
                '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">'
                f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.6" '
                'stroke-linecap="round" stroke-linejoin="round"/></svg>'
            )
    for name, path in SCROLL_ARROWS.items():
        ans[name] = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="6" height="6" viewBox="0 0 6 6">'
            f'<path d="{path}" fill="{T["fg"]}" fill-opacity="{SCROLL_THUMB_ALPHA}"/></svg>'
        )
    return ans


# The shadows of Lectrix's tool cards, as CSS box-shadows: (x, y, blur, spread, (r, g, b, a)).
# At rest --lectrix-shadow-rest, a soft glow under the card; under the pointer, and pressed,
# --lectrix-shadow-hover.
CARD_SHADOWS = {
    'light': {
        'rest': (0, 6, 20, -10, (15, 37, 88, 0.1)),
        'hover': (0, 8, 24, 0, (15, 37, 88, 0.14)),
    },
    'dark': {
        'rest': (0, 6, 20, -10, (0, 0, 0, 0.5)),
        'hover': (0, 8, 24, 0, (0, 0, 0, 0.55)),
    },
}
# A card lifts this many pixels under the pointer, and pressed (translateY(-3px), (-1px)),
# and pressed it sinks back a little (scale(0.98)).
CARD_LIFT = {'rest': 0, 'hover': 3, 'pressed': 1}
CARD_PRESSED_SCALE = 0.98
# The ripple a press sends across a card (--lectrix-ripple, in both modes): a 10 px dot where
# it was pressed, grown 48 times as it fades from 55% (--lectrix-duration-slow, ease-out).
CARD_RIPPLE = (111, 163, 239, 0.35)
CARD_RIPPLE_DOT = 10
CARD_RIPPLE_GROWTH = 48
CARD_RIPPLE_OPACITY = 0.55
CARD_RIPPLE_MS = 400
CSS_EASE_OUT = (0, 0, 0.58, 1)
# How a card moves between them, and its shadow changes: --lectrix-duration-base and
# --lectrix-ease-out, a cubic-bezier().
CARD_MOTION_MS = 250
CARD_EASE = (0.2, 0.8, 0.2, 1)
# The room round a card: half of the 12 px gap between Lectrix's cards.
CARD_MARGIN = 6


def stylesheet(mode, arrow):
    '''Added to calibre's own stylesheet. arrow(name) gives an arrow's image path, for the
    names arrow_images() gives.'''
    T, B = TOKENS[mode], BLENDS[mode]
    return f'''
/* Fields: the surface with a thin edge, a step stronger under the pointer, the accent when
   focused. */
QLineEdit, QAbstractSpinBox, QComboBox {{
    background-color: {T['surface']};
    color: {T['fg']};
    border: 1px solid {T['line']};
    border-radius: 6px;
    padding: 3px 6px;
    selection-background-color: {B['text_selection']};
    selection-color: {T['fg_strong']};
}}
QLineEdit:hover, QAbstractSpinBox:hover, QComboBox:hover {{
    border-color: {T['line_strong']};
}}
QLineEdit:focus, QAbstractSpinBox:focus, QComboBox:focus, QComboBox:on {{
    border-color: {T['accent']};
}}
QLineEdit:disabled, QAbstractSpinBox:disabled, QComboBox:disabled {{
    color: {B['disabled']};
    border-color: {T['line']};
}}
/* The text box inside an editable dropdown or a number field: the outer box has the edge. */
QComboBox QLineEdit, QAbstractSpinBox QLineEdit {{
    background-color: transparent;
    border: none;
    border-radius: 0;
    padding: 0;
}}
/* Dropdowns, as Lectrix's: one you can't type in is a button showing the choice, a step
   lighter under the pointer. Open, a dropdown has a 2 px accent edge, and so does one you
   type in while it has the focus, as Lectrix's fields do. The padding gives back the pixel
   the edge takes. The list opens below, rather than over the dropdown with the choice on
   top. */
QComboBox {{
    padding: 3px 6px 3px 8px;
    combobox-popup: 0;
}}
QComboBox:!editable {{
    background-color: {T['button']};
}}
QComboBox:!editable:hover {{
    background-color: {T['button_hover']};
}}
QComboBox:!editable:disabled {{
    background-color: {B['button_disabled']};
}}
QComboBox:on, QComboBox:editable:focus {{
    border: 2px solid {T['accent']};
    padding: 2px 5px 2px 7px;
}}
/* Editing a cell in a list: no room for padding, round corners or a wider edge. */
QAbstractItemView QLineEdit, QAbstractItemView QAbstractSpinBox, QAbstractItemView QComboBox,
QAbstractItemView QComboBox:on, QAbstractItemView QComboBox:editable:focus {{
    border-width: 1px;
    border-radius: 0;
    padding: 0 2px;
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 22px;
    border: none;
}}
QComboBox::down-arrow {{
    image: url({arrow('down')});
    width: 12px;
    height: 12px;
}}
QComboBox::down-arrow:disabled {{
    image: url({arrow('down-disabled')});
}}
/* The list: a menu, with 28 px rows and the menus' faint tint under the pointer. */
QComboBox QAbstractItemView {{
    background-color: {T['menu']};
    color: {T['fg']};
    border: 1px solid {T['line_strong']};
    padding: 4px;
    selection-background-color: {B['hover_menu']};
    selection-color: {T['fg']};
    outline: 0;
}}
QComboBox QAbstractItemView::item {{
    min-height: 28px;
    padding: 0 8px 0 10px;
    border: none;
    border-radius: 4px;
    color: {T['fg']};
}}
QComboBox QAbstractItemView::item:selected, QComboBox QAbstractItemView::item:hover {{
    background-color: {B['hover_menu']};
    color: {T['fg']};
}}
QComboBox QAbstractItemView::item:disabled {{
    color: {B['disabled']};
}}
QAbstractSpinBox {{
    padding-right: 20px;
}}
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{
    subcontrol-origin: border;
    width: 20px;
    border: none;
    background-color: transparent;
}}
QAbstractSpinBox::up-button {{
    subcontrol-position: top right;
    border-top-right-radius: 6px;
}}
QAbstractSpinBox::down-button {{
    subcontrol-position: bottom right;
    border-bottom-right-radius: 6px;
}}
QAbstractSpinBox::up-button:hover, QAbstractSpinBox::down-button:hover {{
    background-color: {B['hover_surface']};
}}
QAbstractSpinBox::up-arrow {{
    image: url({arrow('up')});
    width: 10px;
    height: 10px;
}}
QAbstractSpinBox::down-arrow {{
    image: url({arrow('down')});
    width: 10px;
    height: 10px;
}}
QAbstractSpinBox::up-arrow:disabled, QAbstractSpinBox::up-arrow:off {{
    image: url({arrow('up-disabled')});
}}
QAbstractSpinBox::down-arrow:disabled, QAbstractSpinBox::down-arrow:off {{
    image: url({arrow('down-disabled')});
}}

/* Buttons: flat, with the same thin edge. The default button of a dialog takes the accent,
   as Lectrix's primary buttons do. */
QPushButton {{
    background-color: {T['button']};
    color: {T['fg']};
    border: 1px solid {T['line']};
    border-radius: 6px;
    padding: 4px 12px;
    min-width: 56px;
}}
QPushButton:hover {{
    background-color: {T['button_hover']};
    border-color: {T['line_strong']};
}}
QPushButton:pressed, QPushButton:checked {{
    background-color: {B['selected']};
    border-color: {T['line_strong']};
}}
QPushButton:default {{
    background-color: {T['accent']};
    color: {T['accent_fg']};
    border-color: {T['accent']};
}}
QPushButton:default:hover {{
    background-color: {B['accent_hover']};
    border-color: {B['accent_hover']};
}}
QPushButton:disabled {{
    background-color: {B['button_disabled']};
    color: {B['disabled']};
    border-color: {T['line']};
}}
QPushButton:focus {{
    border-color: {T['accent']};
}}
QPushButton::menu-indicator {{
    image: url({arrow('down')});
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 10px;
    height: 10px;
    right: -6px;
}}

/* Scrollbars: 10 px, no track, a 6 px rounded thumb, and a triangle in a 12 px button at
   each end. */
QScrollBar {{
    background: transparent;
    border: none;
}}
QScrollBar:vertical {{
    width: 10px;
    padding: 12px 0;
}}
QScrollBar:horizontal {{
    height: 10px;
    padding: 0 12px;
}}
QScrollBar::handle {{
    background: {rgba(T['fg'], SCROLL_THUMB_ALPHA)};
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    margin: 0 2px;
    min-height: 24px;
}}
QScrollBar::handle:horizontal {{
    margin: 2px 0;
    min-width: 24px;
}}
QScrollBar::handle:hover, QScrollBar::handle:pressed {{
    background: {rgba(T['fg'], SCROLL_THUMB_HOVER_ALPHA)};
}}
QScrollBar::add-page, QScrollBar::sub-page {{
    background: transparent;
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    background: transparent;
    border: none;
    subcontrol-origin: border;
}}
QScrollBar::sub-line:vertical {{
    subcontrol-position: top;
    height: 12px;
}}
QScrollBar::add-line:vertical {{
    subcontrol-position: bottom;
    height: 12px;
}}
QScrollBar::sub-line:horizontal {{
    subcontrol-position: left;
    width: 12px;
}}
QScrollBar::add-line:horizontal {{
    subcontrol-position: right;
    width: 12px;
}}
QScrollBar::up-arrow, QScrollBar::down-arrow, QScrollBar::left-arrow, QScrollBar::right-arrow {{
    width: 6px;
    height: 6px;
}}
QScrollBar::up-arrow {{
    image: url({arrow('scroll-up')});
}}
QScrollBar::down-arrow {{
    image: url({arrow('scroll-down')});
}}
QScrollBar::left-arrow {{
    image: url({arrow('scroll-left')});
}}
QScrollBar::right-arrow {{
    image: url({arrow('scroll-right')});
}}
QAbstractScrollArea::corner {{
    background: transparent;
    border: none;
}}
/* The track is the background of what scrolls: the surface of lists and text, the chrome of
   the Tag browser and Book details (calibre's TagsView and BookInfo). */
QAbstractItemView QScrollBar, QAbstractItemView::corner,
QTextEdit QScrollBar, QTextEdit::corner, QPlainTextEdit QScrollBar, QPlainTextEdit::corner {{
    background: {T['surface']};
}}
TagsView QScrollBar, TagsView::corner, BookInfo QScrollBar, BookInfo::corner {{
    background: {T['chrome']};
}}
QComboBox QAbstractItemView QScrollBar {{
    background: {T['menu']};
}}

/* The book list: no frame, so it meets the side panels at their edge line, as the pages meet
   Lectrix's side panes. */
BooksView {{
    border: none;
}}

/* Column headers, the book list's among them: no fill of their own, muted text over a thin
   line, as Lectrix's tables have, with faint lines between columns to resize them by. */
QHeaderView {{
    background-color: {T['surface']};
    border: none;
}}
QHeaderView::section, QTableCornerButton::section {{
    background-color: {T['surface']};
    color: {T['fg_muted']};
    border: none;
    border-right: 1px solid {T['line']};
    border-bottom: 1px solid {T['line']};
    padding: 4px 6px;
}}
QHeaderView::section:hover {{
    background-color: {B['hover_surface']};
    color: {T['fg']};
}}
QHeaderView::up-arrow, QHeaderView::down-arrow {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 10px;
    height: 10px;
    padding-right: 4px;
}}
QHeaderView::up-arrow {{
    image: url({arrow('up')});
}}
QHeaderView::down-arrow {{
    image: url({arrow('down')});
}}

/* The selected tab: outlined in Lectrix's line color rather than calibre's grey. */
QTabBar::tab:selected {{
    border-color: {T['line_strong']};
}}

/* calibre's Preferences: each page a card, as the tools on Lectrix's start screen. chrome.py
   sizes them, paints their shadows and their edge, which fades to blue under the pointer,
   and moves them. */
Browser Category QToolButton {{
    background-color: {T['raised']};
    color: {T['fg_strong']};
    border: 1px solid transparent;
    border-radius: 12px;
    margin: {CARD_MARGIN}px;
    padding: 8px 12px;
}}

/* The toolbar's edge. */
QToolBar {{
    background-color: {T['chrome']};
    border: none;
    border-bottom: 1px solid {T['line']};
}}

/* Menus and tooltips: flat, in the menus' color with a thin edge, hover a faint tint rather
   than the selection color. */
QMenu {{
    background-color: {T['menu']};
    color: {T['fg']};
    border: 1px solid {T['line_strong']};
    padding: 4px;
}}
QMenu::item {{
    background-color: transparent;
    padding: 5px 24px 5px 8px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background-color: {B['hover_menu']};
    color: {T['fg_strong']};
}}
QMenu::item:disabled {{
    color: {B['disabled']};
    background-color: transparent;
}}
QMenu::separator {{
    height: 1px;
    background-color: {T['line']};
    margin: 4px 6px;
}}
QToolTip {{
    background-color: {T['menu']};
    color: {T['fg']};
    border: 1px solid {T['line_strong']};
    padding: 3px 6px;
}}
'''


def card_edge(mode, raised):
    "A Preferences card's edge: the line color at rest, Lectrix's card hover line raised, between."
    T = TOKENS[mode]
    a, b = T['line'], T['card_hover_line']
    rgb = [round(int(a[i:i + 2], 16) + (int(b[i:i + 2], 16) - int(a[i:i + 2], 16)) * raised) for i in (1, 3, 5)]
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def card_shadow(mode, raised):
    """A Preferences card's shadow: at rest for raised 0, under the pointer for 1, and part
    way between, as CSS moves from one box-shadow to another, for what lies between."""
    rest, hover = CARD_SHADOWS[mode]['rest'], CARD_SHADOWS[mode]['hover']
    if raised <= 0:
        return rest
    if raised >= 1:
        return hover
    nums = tuple(a + (b - a) * raised for a, b in zip(rest[:4], hover[:4]))
    r, g, b = (round(a + (b - a) * raised) for a, b in zip(rest[4][:3], hover[4][:3]))
    alpha = rest[4][3] + (hover[4][3] - rest[4][3]) * raised
    return nums + ((r, g, b, alpha),)


def shadow_extent(shadow):
    "How far a box-shadow can reach past its box, on any side."
    x, y, blur, spread, _ = shadow
    return int(blur * 1.5 + max(spread, 0) + max(abs(x), abs(y))) + 1


def shadow_profile(length, start, end, sigma, samples):
    """A box-shadow across one axis: how much of it there is at evenly spaced points along
    length, for a box from start to end blurred as CSS blurs it (a Gaussian with sigma half
    the blur). Gives (position from 0 to 1, amount from 0 to 1) pairs."""
    import math

    ans = []
    for i in range(samples + 1):
        t = i / samples
        pos = t * length
        if end <= start:
            v = 0.0
        elif sigma <= 0:
            v = 1.0 if start <= pos <= end else 0.0
        else:
            k = sigma * math.sqrt(2)
            v = 0.5 * (math.erf((pos - start) / k) - math.erf((pos - end) / k))
        ans.append((t, max(0.0, min(1.0, v))))
    return ans


def hover_text(mode):
    "The Tag browser's hovered text."
    return TOKENS[mode]['fg_strong']


def tree_hover_stylesheet(mode):
    "The Tag browser's hover (it sits on the chrome), in place of calibre's."
    return f'''
    QTreeView::item:hover {{
        background: {BLENDS[mode]['hover_chrome']};
        border: 0px;
        border-radius: 6px;
    }}
'''


# The Edit book syntax themes. Tags take the accent; attributes, strings, entities and
# numbers take Neo's purple, green, pink and orange.
EDITOR_THEME_NAMES = {'light': '*Lectrix light', 'dark': '*Lectrix dark'}


def editor_theme(mode):
    'The theme in the form calibre saves custom editor themes.'
    T, B = TOKENS[mode], BLENDS[mode]
    theme = {
        'Normal': dict(fg=T['fg'], bg=T['surface']),
        'Cursor': dict(bg=T['accent']),
        'CursorLine': dict(bg=T['chrome']),
        'CursorColumn': dict(bg=T['chrome']),
        'ColorColumn': dict(bg=T['chrome']),
        'HighlightRegion': dict(bg=B['selected']),
        'MatchParen': dict(fg=T['fg_strong'], bg=B['emphasis']),
        'Visual': dict(fg=T['fg_strong'], bg=B['text_selection']),
        'LineNr': dict(fg=B['line_number'], bg=T['chrome']),
        'LineNrC': dict(fg=T['fg_strong']),
        'Pmenu': dict(fg=T['fg'], bg=T['menu']),
        'PmenuSel': dict(fg=T['fg_strong'], bg=B['hover_menu']),
        'Tooltip': dict(fg=T['fg'], bg=T['menu']),
        'Comment': dict(fg=B['comment'], italic=True),
        'Todo': dict(fg=T['fg_muted'], bold=True),
        'String': dict(fg=T['green']),
        'Constant': dict(fg=T['orange']),
        'Number': dict(fg=T['orange']),
        'PreProc': dict(fg=T['purple']),
        'Identifier': dict(fg=T['teal']),
        'Function': dict(fg=T['accent']),
        'Type': dict(fg=T['purple']),
        'Statement': dict(fg=T['purple']),
        'Keyword': dict(fg=T['purple']),
        'Special': dict(fg=T['pink']),
        'SpecialCharacter': dict(bg=B['emphasis']),
        'Error': dict(underline='wave', underline_color=T['danger']),
        'SpellError': dict(underline='wave', underline_color=T['orange']),
        'Link': dict(fg=T['blue']),
        'BadLink': dict(fg=T['blue'], underline='wave', underline_color=T['danger']),
        'DiffDelete': dict(fg=T['diff_deleted'], bg=B['diff_deleted_bg']),
        'DiffInsert': dict(fg=T['diff_inserted'], bg=B['diff_inserted_bg']),
        'DiffReplace': dict(fg=T['accent'], bg=B['diff_replaced_bg']),
        'DiffReplaceReplace': dict(bg=B['text_selection']),
    }
    blank = dict(fg=None, bg=None, bold=False, italic=False, underline=None, underline_color=None)
    return {name: {**blank, **attrs} for name, attrs in theme.items()}
