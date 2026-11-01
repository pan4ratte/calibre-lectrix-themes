#!/usr/bin/env python3
# Builds the palette file and both plugin zips from src/:
#   lectrix.calibre-palette
#   dist/lectrix-themes.zip            (calibre's main window)
#   dist/lectrix-themes-edit-book.zip  (the book editor)
# Run: python build.py

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'src'
DIST = ROOT / 'dist'
SHARED = ('lectrix_theme.py', 'chrome.py')

PLUGINS = {
    'lectrix-themes.zip': ('main_plugin', 'lectrix_themes'),
    'lectrix-themes-edit-book.zip': ('editor_plugin', 'lectrix_themes_editor'),
}


def build_palette():
    sys.path.insert(0, str(SRC))
    from lectrix_theme import MODES, palette

    data = {mode: {'use_custom': True, 'palette': dict(sorted(palette(mode).items()))} for mode in MODES}
    out = ROOT / 'lectrix.calibre-palette'
    out.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print('Wrote', out.name)


def build_plugins():
    DIST.mkdir(exist_ok=True)
    for zip_name, (folder, import_name) in PLUGINS.items():
        out = DIST / zip_name
        with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in sorted((SRC / folder).glob('*.py')):
                zf.write(f, f.name)
            for name in SHARED:
                zf.write(SRC / name, name)
            zf.writestr(f'plugin-import-name-{import_name}.txt', '')
        print('Wrote', out.relative_to(ROOT))


if __name__ == '__main__':
    build_palette()
    build_plugins()
