# Lectrix themes for Calibre

Lectrix's light and dark themes for calibre. Lectrix's colors come from Neo's light and Midnight themes for Obsidian, tinted toward Lectrix blue. Calibre uses the theme that matches its mode, and switches when the mode changes.

The themes come as two plugins:

- **Lectrix themes**: sets calibre's light and dark colors to Lectrix's, and styles what the colors alone can't reach in the main window and its dialogs. That means the title bar, fields, buttons, menus, tooltips, scrollbars, the toolbar's edge, the side panels' edges, the book list's column headers, the Tag browser's hover and the book list's current cell.
- **Lectrix themes for Edit book**: the same styling for the book editor, plus "Lectrix light" and "Lectrix dark" syntax themes.

Needs calibre 7 or newer. The title bar colors and the round corners of menus and dropdown lists need Windows 11.

## Install

1. Download `lectrix-themes.zip` and `lectrix-themes-edit-book.zip` from the [latest release](https://github.com/pan4ratte/calibre-lectrix-themes/releases/latest).
2. In calibre, go to Preferences → Plugins → **Load plugin from file**, and load both zips. Restart calibre.
3. In Preferences → Look & feel → Main interface, make sure "User interface style" is **calibre**. Calibre ignores custom colors with the "System" style.

Calibre's mode is set under **Adjust colors** → "Color palette": Light, Dark, or System default to follow Windows.

### The colors

Lectrix themes sets the light and dark colors in Adjust colors to Lectrix's on its first start, and again only when an update changes them. Changes you make in Adjust colors in between are kept. All of calibre's windows read these colors, the e-book viewer and the editor included.

### Turning it off

Untick **Use the Lectrix theme** in Preferences → Plugins → Lectrix themes → **Customize plugin**. Everything is undone at once:

- the colors you had before come back, in both modes;
- the title bar, field, button and menu styling goes;
- the book editor goes back to calibre's automatic syntax theme, the next time it starts.

Calibre doesn't tell plugins when they're removed, so untick this before removing the plugin. If you already removed it, use Adjust colors → **Restore defaults**.

### Colors only, without the plugins

`lectrix.calibre-palette`, also in the release, holds the same light and dark colors for calibre's own palette import. Click **Adjust colors**, then **Import**, and choose the file. You get Lectrix's colors without the title bar, field and menu styling.

## Pairs well with Calibre Modern GNOME

[Calibre Modern GNOME](https://github.com/pan4ratte/calibre-modern-gnome) is a separate icon theme by the same author. It uses clean, modern icons based on Ubuntu's Yaru-Blue style and suits the themes' flat look. It's a separate project, so each works without the other.

The theme is in alpha testing and has no release package yet. Until it does, install it with calibre's own way of replacing icons:

1. In calibre, open Preferences → Advanced → Miscellaneous, and click **Open calibre configuration folder**.
2. Create a `resources` folder there if it doesn't exist. Copy the theme's `images` folder into it, so the icons end up in `resources/images`.
3. Restart calibre.

To go back to calibre's own icons, delete `resources/images` and restart.

## What each part covers

| Part | What it does |
| --- | --- |
| Colors | Window, lists, text, selection, links and tooltips, set in calibre's palette |
| Title bar | Matches the toolbar, with Lectrix's title color and a thin window edge. Covers the main window and every dialog. |
| Fields | Thin edge, stronger under the pointer and in the accent when focused |
| Dropdowns | As in Lectrix: one you can't type in looks like a button, and an open one has a 2 px accent edge. The list opens below, styled as a menu with round corners, with a faint tint under the pointer. |
| Buttons | Flat, with the same edge. A dialog's default button (usually OK) takes the accent. |
| Menus and tooltips | Lectrix's menu color with a thin edge and round corners on menus, separators in the line color, and a faint hover rather than the selection color |
| Toolbar and tabs | The toolbar's lower edge and the selected tab's outline in Lectrix's line color |
| Side panels | The Tag browser and Book details end in a thin line where they meet the book list, as Lectrix's side panes do, in the accent under the pointer. Calibre's own handles are bars with dots. |
| Scrollbars | Thin, as in Lectrix: no track, a rounded thumb in the text color that gets stronger under the pointer, and a small arrow at each end |
| Column headers | The book list's and other lists' headers: muted text over a thin line, faint lines between columns, and Lectrix arrows for the sort order |
| Tag browser | A faint hover. Calibre's own hover in dark mode is brighter than the selection, with black text. |
| Book list's current cell | Looks like the rest of the selected row. Calibre's own style draws it lighter, with black text in dark mode. |
| Book editor | Title bar, fields, buttons, menus, scrollbars and column headers as above, plus the Lectrix syntax themes |
| E-book viewer | Its default "System" color scheme already uses the palette for pages, text and links |

The editor plugin selects the Lectrix syntax theme on its first start, and swaps between the light and dark one as calibre's mode changes. If you pick another theme in the editor's Preferences → Editor settings, that one stays. The plugin rewrites the two Lectrix themes at each start, so changes to them are lost. To make your own version, create a new theme based on one of them under another name.

### Not covered

- **The e-book viewer's title bar.** Calibre doesn't load plugins in the viewer.
- **Buttons calibre styles itself.** Calibre gives some controls their own styling, for example the cover buttons in the metadata editor, and those keep calibre's look.
- **Tight editable dropdowns.** An editable dropdown squeezed down to the width of its text cuts off a sliver of its first letter. Qt gives styled dropdowns no room for the text box's inner margin. It doesn't happen in calibre's stretched fields, such as the search bar.

## How the palette maps

Calibre's 16 palette colors each take a Lectrix design token from `src/app.css`:

| Calibre role | Used for | Lectrix token | Light | Dark |
| --- | --- | --- | --- | --- |
| Window | Main window, toolbars, panes | `--lectrix-chrome` | `#f2f4f7` | `#131416` |
| Base | Book list, text fields | `--lectrix-surface` | `#f9fafb` | `#0c0d0e` |
| AlternateBase | Alternate rows | `--lectrix-chrome` | `#f2f4f7` | `#131416` |
| Button | Buttons | `--lectrix-button` | `#f2f4f7` | `#262a31` |
| ToolTipBase | Tooltips | `--lectrix-menu` | `#e4e9f1` | `#1c1e22` |
| Highlight | Selected rows | `--lectrix-row-selected` on chrome | `#d3dceb` | `#222b39` |
| Accent | Checkboxes, progress, focus | `--lectrix-accent` | `#2f5daa` | `#6fa3ef` |
| WindowText, Text, ButtonText, ToolTipText | Text | `--lectrix-fg` | `#22252a` | `#a9b0bc` |
| HighlightedText, BrightText | Text on a selection, emphasis | `--lectrix-fg-strong` | `#121417` | `#e1e5ea` |
| PlaceholderText | Field hints | `--lectrix-fg-muted` | `#505762` | `#929baa` |
| Any text, disabled | Unavailable controls | `--lectrix-fg` at 45% on chrome | `#94979b` | `#565a61` |
| Link | Links | `--lectrix-accent` | `#2f5daa` | `#6fa3ef` |
| LinkVisited | Visited links | `--lectrix-source-5` (Neo purple) | `#6f55f1` | `#9580ff` |

## Building

All colors live in [src/lectrix_theme.py](src/lectrix_theme.py). `python build.py` writes the palette file from it and packs both plugins into `dist/`. Each plugin carries a copy of the shared modules, `lectrix_theme.py` and `chrome.py`. The main plugin notices any change to the palette colors there and applies them again after an update.

## License

GPL v3, like calibre itself. See [LICENSE](LICENSE).
