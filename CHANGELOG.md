# Changelog


## 1.3.0

### UI/UX improvements

* Tabs look like Lectrix's: pills, the selected one raised, ringed with a thin line in light mode, the others plain until hovered. The page under the tabs is the window's color in a thin, rounded edge instead of a light grey, and so is the page beside the list in Preferences → Look & feel.
* Checkboxes look like Lectrix's: a box with round corners, edged in the muted text color, filled with the accent and ticked when on. Lists with checkboxes and groups that can be switched off have the same box.

## 1.2.0

### New features

* A **Lectrix themes** button on the main toolbar. Clicking it switches calibre between light and dark. Right-clicking it opens a menu to pick Light, Dark or System default, or turn the theme or its font on and off. If you're updating, the button is added at the end of the toolbar once; you can move or remove it in Preferences → Toolbars & menus.
* Lectrix's interface font, Google Sans Text, comes with both plugins and is calibre's interface font while the theme is on, in the main window and the book editor. A font you picked in Look & feel → Main interface stays. Untick **Use Lectrix's font** in the button's menu to keep calibre's font.

### UI/UX improvements

* Preferences shows its pages as a grid of cards with the name beside the icon, as Lectrix's start screen shows its tools: a thin edge, round corners and Lectrix's soft shadow. As in Lectrix, a card rises smoothly under the pointer, with a deeper shadow and its edge fading to blue, and sinks back a little when pressed, with a ripple running out from where it was clicked. The lines between categories are gone. Calibre's own are flat buttons stretched across the window.


## 1.1.0

### UI/UX improvements

* The Tag browser and Book details now end in a thin line where they meet the book list, as Lectrix's side panes do, instead of calibre's bars with dots. The line takes the accent color under the pointer, so it's clear where to drag to resize a panel.
* Scrollbars look like Lectrix's: thin, with no track, a rounded thumb in the text color that gets stronger under the pointer, and a small arrow at each end.
* The column headers of the book list, and of lists in dialogs, are themed: muted text over a thin line, faint lines between columns, and Lectrix arrows for the sort order.
* The book list no longer has a frame around it.
* Dropdowns look like Lectrix's. One you can't type in looks like a button, and it gets a thicker accent edge while open, as does one you're typing in. The list opens below the dropdown instead of over it, styled as a menu, with taller rows and a faint tint under the pointer.
* Menus and dropdown lists have round corners, as in Lectrix. This needs Windows 11.


## 1.0.0

First release.

* **Lectrix themes** sets calibre's light and dark colors to Lectrix's, and styles the title bar, fields, buttons, menus, tooltips, the toolbar's edge, the Tag browser's hover and the book list's current cell to match.
* **Lectrix themes for Edit book** brings the same styling to the book editor, with "Lectrix light" and "Lectrix dark" syntax themes that follow calibre's mode.
* `lectrix.calibre-palette` holds the same colors for calibre's palette import, for those who want only the colors.
