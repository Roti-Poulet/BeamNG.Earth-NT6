"""build_sign_glyphs.py: the highway signs' lettering atlas from the bundled Roadgeek 2014 Series EEM font
(tools/fonts/RG2014EEM.ttf, MIT, https://github.com/sammdot/roadgeek-fonts/releases/tag/3.1: byte-identical to that
release's RG2014-3.10.zip), the FHWA Series E(Modified) alphabet of US guide signs.

    python3 tools/build_sign_glyphs.py

Writes server/sign_glyphs.json (per character: advance, bbox [l, t, r, b] in px from the pen on the baseline, uv
[u0, v0, u1, v1] in the atlas) and the opacity atlas mod/.../roadside/sign_letters_o.data.png, read by the exit,
overhead, merge and mile-marker meshes (server/exitsigns.py lettering()). Every character the font maps is packed in
code point order on fixed-height shelves: the same font file and Pillow/FreeType give the same bytes. Runtime never
renders text: it places atlas quads.

(PR #363 shipped a second atlas, exit_letters_o.data.png with exit_glyphs.json, whose 916 glyphs are not this font's
and whose source font is not stated: replaced by this one.)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "tools", "fonts", "RG2014EEM.ttf")
ATLAS = os.path.join(ROOT, "mod", "beamng_earth", "levels", "beamng_earth", "art", "shapes", "beamngEarth",
                     "roadside", "sign_letters_o.data.png")
METRICS = os.path.join(ROOT, "server", "sign_glyphs.json")
SIZE = (2048, 1024)     # atlas px (width, height; powers of two)
PX = 112                # font size px: the cap height is ~65 px
PAD = 6                 # px between glyphs (mip levels down to 1/8 keep them apart)


def chars(font_path):
    """The characters the font maps (its best cmap), printable ones only, in code point order."""
    from fontTools.ttLib import TTFont
    cmap = TTFont(font_path).getBestCmap()
    return [chr(c) for c in sorted(cmap) if chr(c).isprintable() and c != 0xAD]


def build(font_path=FONT, size=SIZE, px=PX):
    font = ImageFont.truetype(font_path, px)
    ascent, descent = font.getmetrics()
    row = ascent + descent + PAD
    sw, sh = size
    image = Image.new("L", (sw, sh), 0)
    draw = ImageDraw.Draw(image)
    glyphs = {}
    x, y = PAD, PAD
    for c in chars(font_path):
        l, t, r, b = font.getbbox(c, anchor="ls")
        w = r - l
        if x + w + PAD > sw:
            x, y = PAD, y + row
        if y + row > sh:
            raise ValueError("atlas full: lower PX")
        if w > 0 and b > t:
            # the glyph's box top-left at (x, y + ascent + t): every shelf shares one baseline at y + ascent
            top = y + ascent + t
            draw.text((x - l, y + ascent), c, font=font, fill=255, anchor="ls")
            uv = [x / sw, 1 - (top + b - t) / sh, (x + w) / sw, 1 - top / sh]
            x += w + PAD
        else:
            uv = [0.0, 0.0, 0.0, 0.0]
        glyphs[c] = {"advance": round(font.getlength(c), 3), "bbox": [l, t, r, b], "uv": [round(v, 6) for v in uv]}
    cap = -font.getbbox("H", anchor="ls")[1]
    meta = {"font": "Roadgeek 2014 Series EEM", "version": "3.1", "license": "MIT",
            "source": "https://github.com/sammdot/roadgeek-fonts/releases/tag/3.1", "capHeight": cap,
            "glyphs": glyphs}
    return image, meta


def main():
    image, meta = build()
    os.makedirs(os.path.dirname(ATLAS), exist_ok=True)
    image.save(ATLAS, optimize=True)
    with open(METRICS, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(meta, separators=(",", ":"), ensure_ascii=False, sort_keys=True) + "\n")
    print(f"{len(meta['glyphs'])} glyphs, cap height {meta['capHeight']} px -> {ATLAS}, {METRICS}")


if __name__ == "__main__":
    sys.exit(main())
