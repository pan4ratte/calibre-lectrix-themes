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


def title_bar(mode):
    'The Windows title bar, for every calibre window.'
    T = TOKENS[mode]
    return {'caption': T['chrome'], 'text': T['fg_strong'], 'border': T['line']}


# Arrows for dropdowns and number fields: Qt stylesheets need image files, which
# chrome.py writes to calibre's cache folder.
ARROWS = {
    'down': 'M3 6l5 5 5-5',
    'up': 'M3 10l5-5 5 5',
}


def arrow_colors(mode):
    return {'': TOKENS[mode]['fg_muted'], '-disabled': BLENDS[mode]['disabled']}


def arrow_svg(path, color):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">'
        f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )


def stylesheet(mode, arrow):
    '''Added to calibre's own stylesheet. arrow(name) gives an arrow's image path, for names
    such as "down" and "up-disabled".'''
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
/* Editing a cell in a list: no room for padding or round corners. */
QAbstractItemView QLineEdit, QAbstractItemView QAbstractSpinBox, QAbstractItemView QComboBox {{
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
QComboBox QAbstractItemView {{
    background-color: {T['menu']};
    color: {T['fg']};
    border: 1px solid {T['line_strong']};
    selection-background-color: {B['hover_menu']};
    selection-color: {T['fg_strong']};
    outline: 0;
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

/* The selected tab: outlined in Lectrix's line color rather than calibre's grey. */
QTabBar::tab:selected {{
    border-color: {T['line_strong']};
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
