#!/usr/bin/env python3
# Makes the plugins' interface font, src/fonts/, from the official Google Sans release:
# Google Sans Text (the cut for text sizes) in regular, italic, bold and bold italic, cut down
# to Latin, Greek and Cyrillic as Lectrix's copy is, without hinting. Other scripts fall back to the system's
# fonts, a character at a time.
#
# The Google logo ligatures (the liga feature: "Glogo" drawn as the Google G, and so on) are
# left out, as calibre shows any text, book titles among it.
#
# Needs fontTools, only to run this: pip install fonttools
# Run: python tools/subset_fonts.py GoogleSans-v14.000.zip OFL.txt
#   the zip from https://github.com/googlefonts/googlesans/releases/tag/v14.000
#   OFL.txt from the repository at that tag

import sys
import zipfile
from io import BytesIO
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'src' / 'fonts'
STYLES = ('Regular', 'Italic', 'Bold', 'BoldItalic')
SOURCE = 'build/GoogleSans/static/GoogleSansText-{}.ttf'

# Latin with its extensions and Vietnamese, Greek, Cyrillic, combining marks, punctuation,
# currency, letterlike symbols, number forms, arrows, math, shapes and dingbats, and the
# Latin ligatures fi and fl.
UNICODES = (
    '0000-036F, 0370-03FF, 0400-052F, 1C80-1C8F, 1D00-1DBF, 1E00-1FFF, 2000-27BF, 2C60-2C7F,'
    ' 2DE0-2DFF, A640-A69F, A720-A7FF, FB00-FB06, FE2E-FE2F, FEFF, FFFD'
)


# The feature listing every alternate, which nothing uses by default and reaches the logos.
LEFT_OUT = {'aalt'}


def is_logo(glyph):
    return 'logo' in glyph.lower()


def layout_features(font):
    tags = set()
    for table in ('GSUB', 'GPOS'):
        if table in font and font[table].table.FeatureList is not None:
            tags.update(r.FeatureTag for r in font[table].table.FeatureList.FeatureRecord)
    return sorted(tags - LEFT_OUT)


def drop_logo_rules(font):
    """Take out every substitution that gives a logo glyph (in liga and calt), and keep the
    rest of those features, such as the fi and fl ligatures. The subsetter then drops the logos."""
    for lookup in font['GSUB'].table.LookupList.Lookup:
        for st in lookup.SubTable:
            if getattr(st, 'ExtSubTable', None) is not None:
                st = st.ExtSubTable
            kind = st.LookupType
            if kind == 1:  # single
                st.mapping = {k: v for k, v in st.mapping.items() if not is_logo(v)}
            elif kind == 2:  # multiple
                st.mapping = {k: v for k, v in st.mapping.items() if not any(map(is_logo, v))}
            elif kind == 3:  # alternate
                st.alternates = {k: [g for g in v if not is_logo(g)] for k, v in st.alternates.items()}
                st.alternates = {k: v for k, v in st.alternates.items() if v}
            elif kind == 4:  # ligature
                ligatures = {k: [lig for lig in v if not is_logo(lig.LigGlyph)] for k, v in st.ligatures.items()}
                st.ligatures = {k: v for k, v in ligatures.items() if v}


def subset_font(data):
    font = TTFont(BytesIO(data))
    drop_logo_rules(font)
    options = subset.Options()
    options.layout_features = layout_features(font)
    options.name_IDs = ['*']
    options.name_languages = ['*']
    options.notdef_outline = True
    # No hinting: its instructions bend the letters to the pixel grid, which at interface sizes
    # on Windows warps them. Browsers, Lectrix among them, draw the plain outlines.
    options.hinting = False
    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=subset.parse_unicodes(UNICODES))
    subsetter.subset(font)
    logos = [name for name in font.getGlyphOrder() if 'logo' in name.lower()]
    if logos:
        sys.exit(f'Logo glyphs left in the font: {logos[:5]}')
    font['post'].formatType = 3.0  # no glyph names: smaller
    out = BytesIO()
    font.save(out)
    return out.getvalue()


def main(zip_path, ofl_path):
    OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        for style in STYLES:
            data = subset_font(zf.read(SOURCE.format(style)))
            dest = OUT / f'GoogleSansText-{style}.ttf'
            dest.write_bytes(data)
            print('Wrote', dest.relative_to(ROOT), len(data) // 1024, 'KB')
    # The repository's OFL.txt at v14.000 opens with Google Sans Flex's copyright line: the
    # fonts' own (name ID 0) goes in its place.
    font_copyright = 'Copyright 2025 The Google Sans Project Authors (https://github.com/googlefonts/googlesans)'
    lines = Path(ofl_path).read_text(encoding='utf-8').splitlines()
    if lines and lines[0].startswith('Copyright'):
        lines[0] = font_copyright
    (OUT / 'OFL.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('Wrote', (OUT / 'OFL.txt').relative_to(ROOT))


if __name__ == '__main__':
    main(*sys.argv[1:3])
