#!/usr/bin/env python3
# Builds the palette file and both plugin zips from src/:
#   lectrix.calibre-palette
#   dist/lectrix-themes.zip            (calibre's main window)
#   dist/lectrix-themes-edit-book.zip  (the book editor)
# Run: python build.py
#      python build.py --install   also closes calibre, installs both zips and starts it again

import json
import shutil
import subprocess
import sys
import time
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


def calibre_running():
    if sys.platform == 'win32':
        out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq calibre.exe', '/NH'], capture_output=True, text=True).stdout
        return 'calibre.exe' in out
    return subprocess.run(['pgrep', '-x', 'calibre'], capture_output=True).returncode == 0


def install_plugins():
    "Close calibre if it's open, install both zips, and start calibre again if it was open."
    if shutil.which('calibre-customize') is None:
        sys.exit('calibre-customize not found: is calibre installed and on PATH?')
    was_running = calibre_running()
    if was_running:
        print('Closing calibre')
        subprocess.run(['calibre-debug', '-s'], check=False)
        for _ in range(60):
            if not calibre_running():
                break
            time.sleep(0.5)
        else:
            sys.exit('calibre did not close; install skipped')
    for zip_name in PLUGINS:
        subprocess.run(['calibre-customize', '-a', str(DIST / zip_name)], check=True)
    if was_running:
        print('Starting calibre')
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
        subprocess.Popen(['calibre'], creationflags=flags, close_fds=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    build_palette()
    build_plugins()
    if '--install' in sys.argv[1:]:
        install_plugins()
