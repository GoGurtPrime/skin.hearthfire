#!/usr/bin/env python3
"""Author Hearthfire's Default*.png fallback icons: an authored flat glyph-on-timber style.

Kodi requests many of these by exact filename directly from the skin's media/ folder (not only via our XML
<texture fallback="...">), so we ship a broad - if simple - set to avoid missing-texture log warnings across
the library/add-on/profile browsers. All baked colors (not colordiffuse-tinted): these sit directly on real
content thumbnails, so they carry their own timber-chip + ember glyph identity.

Run: python3 scripts/render_defaults.py
"""
import pathlib

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "media" / "defaults"
OUT.mkdir(parents=True, exist_ok=True)

SIZE = 256
TIMBER = (51, 35, 26, 255)
BARK = (74, 52, 37, 255)
EMBER = (228, 103, 43, 255)
CREAM = (241, 230, 210, 255)


def base_chip():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([(8, 8), (SIZE - 9, SIZE - 9)], radius=22, fill=TIMBER, outline=BARK, width=4)
    return img, d


def glyph_film(d):
    d.rounded_rectangle([(64, 70), (192, 186)], radius=10, outline=EMBER, width=8)
    for y in (82, 174):
        for x in (78, 110, 142, 166):
            d.rectangle([x, y - 6, x + 14, y + 6], fill=EMBER)


def glyph_tv(d):
    d.rounded_rectangle([(56, 76), (200, 164)], radius=14, outline=EMBER, width=8)
    d.rectangle([110, 172, 146, 190], fill=EMBER)
    d.rectangle([92, 190, 164, 200], fill=EMBER)


def glyph_note(d):
    d.ellipse([(80, 150), (120, 186)], fill=EMBER)
    d.ellipse([(140, 134), (180, 170)], fill=EMBER)
    d.rectangle([(116, 76), (124, 168)], fill=EMBER)
    d.rectangle([(176, 60), (184, 152)], fill=EMBER)
    d.line([(116, 76), (176, 60)], fill=EMBER, width=8)


def glyph_person(d):
    d.ellipse([(98, 68), (158, 128)], outline=EMBER, width=8)
    d.arc([(70, 140), (186, 230)], start=200, end=340, fill=EMBER, width=8)
    d.line([(70, 190), (70, 170)], fill=EMBER, width=8)
    d.line([(186, 190), (186, 170)], fill=EMBER, width=8)


def glyph_folder(d):
    d.polygon([(60, 100), (110, 100), (126, 118), (196, 118), (196, 180), (60, 180)], outline=EMBER, width=8)


def glyph_puzzle(d):
    d.rounded_rectangle([(72, 72), (184, 184)], radius=16, outline=EMBER, width=8)
    d.ellipse([(112, 56), (144, 88)], outline=EMBER, width=8)


def glyph_star(d):
    cx, cy, r1, r2 = 128, 128, 70, 30
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = r1 if i % 2 == 0 else r2
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.polygon(pts, outline=EMBER, width=6)


def glyph_disc(d):
    d.ellipse([(68, 68), (188, 188)], outline=EMBER, width=8)
    d.ellipse([(116, 116), (140, 140)], fill=EMBER)


def glyph_warn(d):
    d.polygon([(128, 60), (196, 186), (60, 186)], outline=EMBER, width=8)
    d.rectangle([(122, 100), (134, 150)], fill=EMBER)
    d.ellipse([(120, 158), (136, 174)], fill=EMBER)


def glyph_info(d):
    d.ellipse([(78, 78), (178, 178)], outline=EMBER, width=8)
    d.rectangle([(122, 110), (134, 150)], fill=EMBER)
    d.ellipse([(120, 88), (136, 104)], fill=EMBER)


GLYPHS = {
    "film": glyph_film, "tv": glyph_tv, "note": glyph_note, "person": glyph_person,
    "folder": glyph_folder, "puzzle": glyph_puzzle, "star": glyph_star, "disc": glyph_disc,
    "warn": glyph_warn, "info": glyph_info,
}

# name -> glyph key. Grouped by theme; covers the common Kodi fallback-icon surface area (diffed against the
# reference skins' media/ directories - this is a practical subset, not the full exhaustive set).
NAMES = {
    "DefaultVideo": "film", "DefaultMovies": "film", "DefaultMovieTitle": "film", "DefaultSets": "film",
    "DefaultVideoCover": "film", "DefaultVideoPlaylists": "film", "DefaultRecentlyAddedMovies": "film",
    "DefaultTVShows": "tv", "DefaultTVShowTitle": "tv", "DefaultRecentlyAddedEpisodes": "tv",
    "DefaultInProgressShows": "tv", "DefaultMusicVideos": "tv", "DefaultRecentlyAddedMusicVideos": "tv",
    "DefaultMusicAlbums": "note", "DefaultMusicArtists": "note", "DefaultMusicSongs": "note",
    "DefaultMusicGenres": "note", "DefaultMusicPlaylists": "note", "DefaultMusicRecentlyAdded": "note",
    "DefaultMusicRecentlyPlayed": "note", "DefaultMusicTop100": "note", "DefaultMusicTop100Albums": "note",
    "DefaultMusicTop100Songs": "note", "DefaultMusicCompilations": "note", "DefaultMusicYears": "note",
    "DefaultMusicSources": "note", "DefaultAlbumCover": "note", "DefaultAudio": "note",
    "DefaultActor": "person", "DefaultDirector": "person", "DefaultUser": "person",
    "DefaultMusicRoles": "person", "DefaultArtist": "person",
    "DefaultFolder": "folder", "DefaultFolderBack": "folder", "DefaultFile": "folder",
    "DefaultPlaylist": "folder", "DefaultNetwork": "folder", "DefaultHardDisk": "folder",
    "DefaultRemovableDisk": "folder", "DefaultAddSource": "folder",
    "DefaultAddon": "puzzle", "DefaultAddonsInstalled": "puzzle", "DefaultAddonsUpdates": "puzzle",
    "DefaultAddonsSearch": "puzzle", "DefaultAddonRepository": "puzzle", "DefaultAddonService": "puzzle",
    "DefaultAddonScreensaver": "puzzle", "DefaultAddonSkin": "puzzle", "DefaultAddonVideo": "puzzle",
    "DefaultAddonMusic": "puzzle", "DefaultAddonProgram": "puzzle", "DefaultAddonPVRClient": "puzzle",
    "DefaultAddonVisualization": "puzzle", "DefaultAddonPicture": "puzzle", "DefaultAddonWeather": "puzzle",
    "DefaultAddonLyrics": "puzzle", "DefaultAddonSubtitles": "puzzle", "DefaultAddonLanguage": "puzzle",
    "DefaultAddonLibrary": "puzzle", "DefaultAddonInfoProvider": "puzzle", "DefaultAddonNone": "puzzle",
    "DefaultProgram": "puzzle", "DefaultScript": "puzzle", "DefaultGames": "puzzle",
    "DefaultFavourites": "star", "DefaultGenre": "star", "DefaultTags": "star",
    "DefaultYear": "disc", "DefaultCountry": "disc", "DefaultStudios": "disc", "DefaultPicture": "disc",
    "DefaultDVDFull": "disc", "DefaultDVDEmpty": "disc", "DefaultDVDRom": "disc", "DefaultCDDA": "disc",
    "DefaultIconWarning": "warn", "DefaultIconError": "warn",
    "DefaultIconInfo": "info",
}


def main() -> None:
    for name, glyph in NAMES.items():
        img, d = base_chip()
        GLYPHS[glyph](d)
        img.save(OUT / f"{name}.png", "PNG", optimize=True)
    print(f"wrote {len(NAMES)} default icons to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
