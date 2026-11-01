from qt.core import QCheckBox, QLabel, QVBoxLayout, QWidget

from .palette import prefs, use_theme


class ConfigWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.use_theme = QCheckBox('Use the Lectrix theme')
        self.use_theme.setChecked(use_theme())
        layout.addWidget(self.use_theme)
        note = QLabel(
            "Sets the light and dark colors in Look & feel → Adjust colors to Lectrix's, and"
            ' styles title bars, fields, buttons and menus to match, in calibre and its editor.'
            ' Turning this off brings back the colors you had before. Turn it off before'
            ' removing the plugin, or the Lectrix colors stay.'
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch()

    def save_settings(self):
        prefs['use_theme'] = self.use_theme.isChecked()
