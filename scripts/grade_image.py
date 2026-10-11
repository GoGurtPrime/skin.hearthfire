#!/usr/bin/env python3
"""Grade generated candidates into final skin assets.

For each image in design/candidates/, depending on its id prefix:
  backdrop_* -> crop/scale to 1920x1080, warm-grade, darken to <=0.18 mean luminance (<=0.12 in text zone),
                re-apply a clean-left gradient, strip metadata, encode progressive JPEG q84
                -> extras/backdrops/bg_<name>.jpg
  tile_*     -> crop to square, scale to 360x480 (matches Settings.xml's 192x300 icon slot plus margin),
                warm-grade lightly, encode PNG -> media/settings/settings_<name>.png
  empty_*    -> scale to 800x500, warm-grade, encode PNG (keeps alpha if present)
                -> extras/empty/empty_<name>.png
  texture_*  -> left as near-passthrough (textures are already non-photographic); PNG
                -> extras/textures/tex_<name>.png

Never hand-edit the extras/media output; re-run this script after regenerating a candidate.
"""
import pathlib
import sys

from PIL import Image, ImageEnhance, ImageOps, ImageStat

ROOT = pathlib.Path(__file__).resolve().parent.parent
CANDIDATES = ROOT / "design" / "candidates"
BACKDROPS_OUT = ROOT / "extras" / "backdrops"
EMPTY_OUT = ROOT / "extras" / "empty"
TEXTURES_OUT = ROOT / "extras" / "textures"
SETTINGS_OUT = ROOT / "media" / "settings"
for d in (BACKDROPS_OUT, EMPTY_OUT, TEXTURES_OUT, SETTINGS_OUT):
    d.mkdir(parents=True, exist_ok=True)

WARM_TINT = (217, 180, 140)  # warm bias tint applied to every graded backdrop/tile before darkening


def strip_metadata(img: Image.Image) -> Image.Image:
    data = list(img.getdata())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)
    return clean


def cover_resize(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Resize+crop to exactly fill target size (aspect-fill / 'cover'), centered."""
    src_w, src_h = img.size
    src_ratio = src_w / src_h
    dst_ratio = target_w / target_h
    if src_ratio > dst_ratio:
        new_h = target_h
        new_w = int(new_h * src_ratio)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def warm_grade(img: Image.Image, strength: float = 0.18) -> Image.Image:
    rgb = img.convert("RGB")
    warm_layer = Image.new("RGB", rgb.size, WARM_TINT)
    return Image.blend(rgb, warm_layer, strength)


def darken_to_luminance(img: Image.Image, target: float = 0.16) -> Image.Image:
    stat = ImageStat.Stat(img.convert("L"))
    mean = stat.mean[0] / 255.0
    if mean <= target:
        return img
    factor = max(0.25, target / mean)
    return ImageEnhance.Brightness(img).enhance(factor)


def apply_clean_left_scrim(img: Image.Image, strength: int = 160) -> Image.Image:
    """Darken the left ~55% of the frame so title text always sits on a clean, low-contrast background."""
    w, h = img.size
    overlay = Image.new("L", (w, h), 0)
    px = overlay.load()
    cutoff = int(w * 0.55)
    for x in range(w):
        if x < cutoff:
            a = strength
        elif x < w:
            a = int(strength * max(0, 1 - (x - cutoff) / (w * 0.15)))
        else:
            a = 0
        for y in range(h):
            px[x, y] = a
    return _blend_scrim(img, overlay)


def _blend_scrim(img: Image.Image, alpha_mask: Image.Image) -> Image.Image:
    base = img.convert("RGBA")
    scrim = Image.new("RGBA", img.size, (8, 5, 4, 0))
    scrim.putalpha(alpha_mask)
    return Image.alpha_composite(base, scrim).convert("RGB")


def grade_backdrop(path: pathlib.Path) -> None:
    name = path.stem.removeprefix("backdrop_")
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    img = cover_resize(img, 1920, 1080)
    img = warm_grade(img, 0.14)
    img = apply_clean_left_scrim(img, strength=150)
    img = darken_to_luminance(img, target=0.16)
    img = strip_metadata(img)
    out = BACKDROPS_OUT / f"bg_{name}.jpg"
    img.save(out, "JPEG", quality=84, optimize=True, progressive=True)
    kb = out.stat().st_size / 1024
    print(f"backdrop -> {out.relative_to(ROOT)} ({kb:.0f} KB)")


def grade_tile(path: pathlib.Path) -> None:
    name = path.stem.removeprefix("tile_settings_")
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    img = cover_resize(img, 360, 480)
    img = warm_grade(img, 0.08)
    img = strip_metadata(img)
    out = SETTINGS_OUT / f"settings_{name}.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"tile -> {out.relative_to(ROOT)}")


def grade_empty(path: pathlib.Path) -> None:
    name = path.stem.removeprefix("empty_")
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    img = cover_resize(img, 800, 500)
    img = warm_grade(img, 0.10)
    img = darken_to_luminance(img, target=0.14)
    img = strip_metadata(img)
    out = EMPTY_OUT / f"empty_{name}.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"empty -> {out.relative_to(ROOT)}")


def grade_texture(path: pathlib.Path) -> None:
    name = path.stem.removeprefix("texture_")
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    img = strip_metadata(img)
    out = TEXTURES_OUT / f"tex_{name}.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"texture -> {out.relative_to(ROOT)}")


DISPATCH = {
    "backdrop_": grade_backdrop,
    "tile_settings_": grade_tile,
    "empty_": grade_empty,
    "texture_": grade_texture,
}


def main() -> int:
    if not CANDIDATES.exists():
        print(f"no candidates dir at {CANDIDATES}", file=sys.stderr)
        return 1
    count = 0
    for path in sorted(CANDIDATES.glob("*.png")):
        for prefix, fn in DISPATCH.items():
            if path.stem.startswith(prefix):
                fn(path)
                count += 1
                break
        else:
            print(f"skip (unrecognized prefix): {path.name}")
    print(f"Graded {count} image(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
