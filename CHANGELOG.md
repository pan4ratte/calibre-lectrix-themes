# Changelog


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
