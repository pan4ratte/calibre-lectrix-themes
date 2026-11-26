#!/usr/bin/env python3
# Makes images/logo.svg, the README header's icon: Calibre Modern GNOME's calibre icon
# (images/calibre.png in that repo) in Lectrix's colors, centered on the Lectrix app icon's tile
# (lectrix/design/app-icon/lectrix-icon.svg: gradient, sheen, rim and the mark's shadow).
#
# The four books are traced from the pack's 256 px icon, with its bands, lettering and ribbon,
# in flat colors: every book the same pale blue, its bands a darker one and its lettering and
# ribbon darker still. The lettering is Google Sans Text Bold from src/fonts, turned into
# outlines so the SVG needs no font.
#
# Run: python tools/make_logo.py
# Needs fontTools.

from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'images' / 'logo.svg'
FONT = ROOT / 'src' / 'fonts' / 'GoogleSansText-Bold.ttf'

TILE = ('M313.68,50.00 c51.92,0 77.88,0 97.70,10.10 a92.70,92.70 0 0 1 40.51,40.51 c10.10,19.83 10.10,45.79 10.10,97.70 '
        'L462.00,313.68 c0,51.92 0,77.88 -10.10,97.70 a92.70,92.70 0 0 1 -40.51,40.51 c-19.83,10.10 -45.79,10.10 -97.70,10.10 '
        'L198.32,462.00 c-51.92,0 -77.88,0 -97.70,-10.10 a92.70,92.70 0 0 1 -40.51,-40.51 c-10.10,-19.83 -10.10,-45.79 -10.10,-97.70 '
        'L50.00,198.32 c0,-51.92 0,-77.88 10.10,-97.70 a92.70,92.70 0 0 1 40.51,-40.51 c19.83,-10.10 45.79,-10.10 97.70,-10.10 Z')

# The books on the pack's 256 px grid: centre, tilt (negative: the top leans left), width and
# length, then each part along the book from its top-left corner. Bands are (top, bottom).
# Lettering reads bottom to top: (text, centre across, centre along, length, size).
BOOKS = [
    dict(centre=(52.5, 127.5), tilt=0, w=49, l=219,
         bands=[(10.5, 20.5), (198, 208)],
         text=[('CALIBRE', 24.9, 143, 90, 22.5)]),
    dict(centre=(102, 133.5), tilt=0, w=43.5, l=208,
         bands=[(21.5, 31.5), (176.5, 187)],
         text=[('Kovid Goyal', 21.5, 119.5, 94, 15.5)]),
    dict(centre=(150.6, 127.3), tilt=-7.99, w=24.5, l=224,
         bands=[(12.5, 23), (198, 206.75)],
         text=[('Mark Ingram', 12.6, 157, 66, 10.5)]),
    dict(centre=(197, 154.8), tilt=-12.02, w=44, l=165,
         bands=[(20, 31), (132.5, 142.5)],
         ribbon=(15, 30, 50, 43.5),  # left, right, bottom at the sides, bottom at the notch
         text=[('Yaru Style', 16.5, 94, 49, 10), ('Calibre Icon', 26.8, 94, 56, 10)]),
]
RADIUS = 3.5
PACK_BOX = (27, 15, 235, 240)  # the drawing's bounds on the pack's grid
ICON_HEIGHT = 0.6  # the books' height, to the icon's

# Lectrix pale blues (lectrix/design/tokens.json, between blue-50 and blue-200)
BOOK = '#E6EFFC'
BAND = '#C4D8F6'
LETTERING = '#93B4E6'
SHADOW = '#0F2E6B', 0.28, 7, 10  # the Lectrix mark's shadow: color, opacity, blur and drop on the 512 grid


class Lettering:
    "Text as outlines, laid out as SVG's text-anchor middle, dominant-baseline central and textLength do."

    def __init__(self, path):
        self.font = TTFont(path)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font['head'].unitsPerEm
        hhea = self.font['hhea']
        self.central = (hhea.ascent + hhea.descent) / 2
        self.paths = {}

    def glyph(self, name):
        if name not in self.paths:
            pen = SVGPathPen(self.glyphs)
            self.glyphs[name].draw(pen)
            self.paths[name] = pen.getCommands()
        return self.paths[name]

    def svg(self, text, size, length):
        names = [self.cmap[ord(ch)] for ch in text]
        advances = [self.glyphs[n].width for n in names]
        scale = size / self.upm
        stretch = length / (sum(advances) * scale)
        parts, x = [], 0
        for name, advance in zip(names, advances):
            d = self.glyph(name)
            if d:
                parts.append(f'<path transform="translate({x} 0)" d="{d}"/>')
            x += advance
        return (f'<g transform="translate({-length / 2:.3f} {self.central * scale:.3f}) '
                f'scale({scale * stretch:.6f} {-scale:.6f})">{"".join(parts)}</g>')


def book_svg(book, index, lettering):
    w, l = book['w'], book['l']
    cx, cy = book['centre']
    place = f'translate({cx} {cy}) rotate({book["tilt"]}) translate({-w / 2} {-l / 2})'
    shape = f'<rect width="{w}" height="{l}" rx="{RADIUS}"/>'
    parts = [f'<clipPath id="book{index}">{shape}</clipPath>',
             f'<rect width="{w}" height="{l}" rx="{RADIUS}" fill="{BOOK}"/>',
             f'<g clip-path="url(#book{index})" fill="{BAND}">']
    for top, bottom in book['bands']:
        parts.append(f'<rect y="{top}" width="{w}" height="{bottom - top:g}"/>')
    if 'ribbon' in book:
        left, right, side, notch = book['ribbon']
        parts.append(f'<path d="M{left},0 H{right} V{side} L{(left + right) / 2},{notch} L{left},{side} Z" fill="{LETTERING}"/>')
    parts.append(f'</g><g fill="{LETTERING}">')
    for text, across, along, length, size in book['text']:
        parts.append(f'<g transform="translate({across} {along}) rotate(-90)">{lettering.svg(text, size, length)}</g>')
    parts.append('</g>')
    return f'<g transform="{place}">{"".join(parts)}</g>', f'<g transform="{place}">{shape}</g>'


def logo_svg():
    lettering = Lettering(FONT)
    x0, y0, x1, y1 = PACK_BOX
    scale = ICON_HEIGHT * 512 / (y1 - y0)
    place = f'translate(256 256) scale({scale:.5f}) translate({-(x0 + x1) / 2} {-(y0 + y1) / 2})'
    books, silhouettes = zip(*(book_svg(b, i, lettering) for i, b in enumerate(BOOKS)))
    color, opacity, blur, drop = SHADOW
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A3C8F9"/><stop offset="1" stop-color="#4A82E0"/></linearGradient>
<radialGradient id="sheen" cx="0.35" cy="0.05" r="0.75"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.35"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>
<linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.95"/><stop offset="0.28" stop-color="#FFFFFF" stop-opacity="0.08"/><stop offset="0.72" stop-color="#FFFFFF" stop-opacity="0.04"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0.6"/></linearGradient>
<clipPath id="tile"><path d="{TILE}"/></clipPath>
<filter id="drop" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{blur}"/></filter>
</defs>
<path d="{TILE}" fill="url(#bg)"/>
<path d="{TILE}" fill="url(#sheen)"/>
<g clip-path="url(#tile)">
<g filter="url(#drop)"><g transform="translate(0 {drop}) {place}" fill="{color}" fill-opacity="{opacity}">{''.join(silhouettes)}</g></g>
<g transform="{place}">{''.join(books)}</g>
<path d="{TILE}" fill="none" stroke="url(#rim)" stroke-width="7"/>
</g>
</svg>
'''


def main():
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(logo_svg(), encoding='utf-8')
    print('Wrote', OUT.relative_to(ROOT))


if __name__ == '__main__':
    main()
