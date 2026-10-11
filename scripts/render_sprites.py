#!/usr/bin/env python3
"""Author Hearthfire's UI chrome sprites as plain white/neutral PNGs (tinted at runtime via <colordiffuse>).

UI sprites and icons are authored, never AI-generated. This script draws every texture referenced from
16x9/*.xml under media/ui/ and media/icons/ using Pillow primitives only (rounded rects, rings, gradients,
simple glyph shapes) - no external art, no AI model calls.

Run: python3 scripts/render_sprites.py
"""
import math
import pathlib

from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
UI = ROOT / "media" / "ui"
ICONS = ROOT / "media" / "icons"
UI.mkdir(parents=True, exist_ok=True)
ICONS.mkdir(parents=True, exist_ok=True)

WHITE = (255, 255, 255, 255)


def save(img: Image.Image, path: pathlib.Path) -> None:
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path.relative_to(ROOT)} {img.size}")


def rounded_rect(size, radius, fill=WHITE, outline=None, outline_width=0):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([(0, 0), (size[0] - 1, size[1] - 1)], radius=radius, fill=fill,
                        outline=outline, width=outline_width)
    return img


def main() -> None:
    # white.png: 1x1-ish solid white base for colordiffuse-tinted fills
    save(Image.new("RGBA", (8, 8), WHITE), UI / "white.png")

    # rounded6.png: card/poster/button radius, 9-slice friendly
    save(rounded_rect((48, 48), radius=10), UI / "rounded6.png")

    # rounded10.png: dialog radius, larger canvas so border=24 reads cleanly
    save(rounded_rect((64, 64), radius=14), UI / "rounded10.png")

    # rounded6_outline.png: ghost button stroke only
    save(rounded_rect((48, 48), radius=10, fill=(0, 0, 0, 0), outline=WHITE, outline_width=3), UI / "rounded6_outline.png")

    # circle.png: icon-button background / mover handles
    img = Image.new("RGBA", (72, 72), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse([(0, 0), (71, 71)], fill=WHITE)
    save(img, UI / "circle.png")

    # rim_ember.png: hairline focus ring. Baked ember->flame diagonal gradient, alpha ring only.
    size = 96
    ember = (228, 103, 43)
    flame = (245, 163, 59)
    grad = Image.new("RGBA", (size, size))
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * (size - 1))
            r = int(ember[0] + (flame[0] - ember[0]) * t)
            g = int(ember[1] + (flame[1] - ember[1]) * t)
            b = int(ember[2] + (flame[2] - ember[2]) * t)
            grad.putpixel((x, y), (r, g, b, 255))
    outer = Image.new("L", (size, size), 0)
    ImageDraw.Draw(outer).rounded_rectangle([(0, 0), (size - 1, size - 1)], radius=14, fill=255)
    inner = Image.new("L", (size, size), 0)
    ImageDraw.Draw(inner).rounded_rectangle([(3, 3), (size - 4, size - 4)], radius=12, fill=255)
    inner_px = inner.load()
    outer_px = outer.load()
    ring = Image.new("L", (size, size), 0)
    ring_px = ring.load()
    for y in range(size):
        for x in range(size):
            ring_px[x, y] = 255 if (outer_px[x, y] and not inner_px[x, y]) else 0
    ring = ring.filter(ImageFilter.GaussianBlur(0.6))
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(grad, (0, 0), ring)
    save(out, UI / "rim_ember.png")

    # bloom_ember.png: soft radial glow, white (tinted via colordiffuse at runtime)
    size = 160
    img = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(img)
    cx = cy = size / 2
    max_r = size / 2
    for radius in range(int(max_r), 0, -1):
        alpha = int(255 * (1 - radius / max_r) ** 1.6)
        d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=alpha)
    glow_rgb = Image.new("RGBA", (size, size), WHITE)
    glow_rgb.putalpha(img)
    save(glow_rgb, UI / "bloom_ember.png")

    # panel_inner_stroke.png: 1px hairline rect just inside the edge, for dialog cards
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([(1, 1), (size - 2, size - 2)], radius=12, outline=WHITE, width=1)
    save(img, UI / "panel_inner_stroke.png")

    # chip_notch.png: ticket-stub chip, rounded rect with small semicircular notches left/right
    w, h = 64, 40
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([(0, 0), (w - 1, h - 1)], radius=10, fill=WHITE)
    notch_r = 7
    d.ellipse([-notch_r, h / 2 - notch_r, notch_r, h / 2 + notch_r], fill=(0, 0, 0, 0))
    d.ellipse([w - notch_r, h / 2 - notch_r, w + notch_r, h / 2 + notch_r], fill=(0, 0, 0, 0))
    save(img, UI / "chip_notch.png")

    # busy_ring.png: a 270 degree arc for the slow-rotating busy indicator
    size = 128
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    stroke = 10
    bbox = [stroke, stroke, size - stroke, size - stroke]
    d.arc(bbox, start=0, end=270, fill=WHITE, width=stroke)
    img = img.filter(ImageFilter.GaussianBlur(0.4))
    save(img, UI / "busy_ring.png")

    # gradient_h.png: horizontal alpha ramp, opaque left -> transparent right
    w, h = 256, 8
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for x in range(w):
        a = int(255 * (1 - x / (w - 1)) ** 1.3)
        for y in range(h):
            img.putpixel((x, y), (255, 255, 255, a))
    save(img, UI / "gradient_h.png")

    # gradient_v.png: vertical alpha ramp, transparent top -> opaque bottom
    w, h = 8, 256
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(h):
        a = int(255 * (y / (h - 1)) ** 1.3)
        for x in range(w):
            img.putpixel((x, y), (255, 255, 255, a))
    save(img, UI / "gradient_v.png")

    # vignette.png: radial darkening toward the corners, stretched to fullscreen in XML
    w, h = 480, 270
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cx, cy = w / 2, h / 2
    max_d = math.hypot(cx, cy)
    for y in range(h):
        for x in range(w):
            d_ = math.hypot(x - cx, y - cy) / max_d
            a = int(max(0, (d_ - 0.55)) / 0.45 * 160)
            a = min(a, 160)
            img.putpixel((x, y), (12, 8, 6, a))
    save(img, UI / "vignette.png")

    # grain.png: sparse static noise, stretched + low alpha in XML
    import random
    random.seed(31416)
    w, h = 480, 270
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for y in range(h):
        for x in range(w):
            if random.random() < 0.10:
                v = random.randint(140, 255)
                px[x, y] = (v, v, v, random.randint(40, 120))
    save(img, UI / "grain.png")

    # scrollbar_thumb.png: small up-chevron used for spin control increment/decrement
    w, h = 32, 20
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(w / 2, 2), (w - 4, h - 4), (4, h - 4)], fill=WHITE)
    save(img, UI / "scrollbar_thumb.png")

    # pointer.png: small flame-tipped arrow cursor glyph
    w, h = 32, 32
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(2, 2), (2, 26), (10, 20), (14, 29), (18, 27), (14, 18), (24, 18)], fill=WHITE)
    save(img, UI / "pointer.png")

    def icon_canvas():
        return Image.new("RGBA", (48, 48), (0, 0, 0, 0))

    # skip_prev: bar + left-pointing triangle
    img = icon_canvas()
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, 13, 38], fill=WHITE)
    d.polygon([(38, 10), (38, 38), (14, 24)], fill=WHITE)
    save(img, ICONS / "skip_prev.png")

    # skip_next: mirror of skip_prev
    img = icon_canvas()
    d = ImageDraw.Draw(img)
    d.rectangle([35, 10, 38, 38], fill=WHITE)
    d.polygon([(10, 10), (10, 38), (34, 24)], fill=WHITE)
    save(img, ICONS / "skip_next.png")

    # rewind: two stacked left triangles
    img = icon_canvas()
    d = ImageDraw.Draw(img)
    d.polygon([(26, 12), (26, 36), (10, 24)], fill=WHITE)
    d.polygon([(42, 12), (42, 36), (26, 24)], fill=WHITE)
    save(img, ICONS / "rewind.png")

    # forward: two stacked right triangles
    img = icon_canvas()
    d = ImageDraw.Draw(img)
    d.polygon([(22, 12), (22, 36), (38, 24)], fill=WHITE)
    d.polygon([(6, 12), (6, 36), (22, 24)], fill=WHITE)
    save(img, ICONS / "forward.png")

    # play_pause: play triangle (static glyph; Kodi swaps the control not the icon in v1)
    img = icon_canvas()
    d = ImageDraw.Draw(img)
    d.polygon([(14, 10), (14, 38), (38, 24)], fill=WHITE)
    save(img, ICONS / "play_pause.png")

    # check: checkmark
    img = icon_canvas()
    d = ImageDraw.Draw(img)
    d.line([(10, 25), (20, 35), (40, 12)], fill=WHITE, width=5, joint="curve")
    save(img, ICONS / "check.png")

    print("Done.")


if __name__ == "__main__":
    main()
