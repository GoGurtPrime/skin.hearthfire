#!/usr/bin/env python3
"""Author resources/icon.png (512x512, solid colors, no transparency - required for repo submission) and a
procedural placeholder resources/fanart.jpg (1920x1080). Both are authored, not AI-generated, matching the
addon-icon convention across other Kodi skins (a simple glyph, not a photo)."""
import pathlib

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "resources"
OUT.mkdir(parents=True, exist_ok=True)

CHAR = (12, 8, 6)
EMBER = (228, 103, 43)
FLAME = (245, 163, 59)


def make_icon():
    size = 512
    img = Image.new("RGB", (size, size), CHAR)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([(96, 160), (416, 416)], radius=24, outline=EMBER, width=14)
    cx = size / 2
    d.polygon([(cx, 200), (cx - 54, 320), (cx - 54, 360), (cx, 400), (cx + 54, 360), (cx + 54, 320)], fill=EMBER)
    d.polygon([(cx, 236), (cx - 28, 320), (cx - 28, 348), (cx, 372), (cx + 28, 348), (cx + 28, 320)], fill=FLAME)
    img.save(OUT / "icon.png", "PNG")
    print("wrote", OUT / "icon.png", img.size, "mode", img.mode)


def make_fanart():
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), CHAR)
    d = ImageDraw.Draw(img)
    cx, cy = int(w * 0.72), int(h * 0.55)
    for r in range(900, 0, -6):
        t = r / 900
        col = tuple(int(CHAR[i] + (EMBER[i] - CHAR[i]) * (1 - t) * 0.5) for i in range(3))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    img.save(OUT / "fanart.jpg", "JPEG", quality=85)
    print("wrote", OUT / "fanart.jpg", img.size)


if __name__ == "__main__":
    make_icon()
    make_fanart()
