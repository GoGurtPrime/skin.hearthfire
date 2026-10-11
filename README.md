# Hearthfire

A dark, warm skin for Kodi, built for a home theater rather than a desktop. Fanart is graded to one
consistent warm look, focus reads as a glowing edge instead of a blue box, and the whole thing is designed to
sit quietly behind whatever you're watching.

Status: early (v0.1.0). Core navigation, library views, playback and settings are all in place and running,
but it hasn't had a proper shakeout on real hardware yet. Expect rough edges.

## Screenshots

Coming once this has had a pass on a real TV. The dev loop below includes a `kodi-send` snapshot command if
you want to grab your own in the meantime.

## What it looks like

- A timber-and-brass navigation rail along the bottom of Home, not the usual sidebar.
- Focus is a thin ember-to-amber glow around the edge of whatever's selected.
- Every backdrop gets the same warm grade and a clean dark zone behind the title text.
- Settings has a row of small picture tiles instead of a flat list, the way a couple of older skins used to
  do it, redone with original artwork.
- Pausing a video swaps the OSD for a ticket-stub style card with your remaining runtime and end time.
- The lights dim to black when playback starts and come back up warm when it stops.

## Requirements

Kodi 21 (Omega) or newer, `xbmc.gui` 5.17.0+. Built and tested against a Raspberry Pi 4 running at 1080p.

## Installing

Grab a release zip and either:

- **Kodi → Settings → Add-ons → Install from zip file**, then browse to wherever you put it, or
- unzip it straight into your addons folder:
  - Raspberry Pi OS / OSMC: `~/.kodi/addons/`
  - LibreELEC: `/storage/.kodi/addons/`

Then **Settings → Interface → Skin → Hearthfire**, and open Skin Settings to pick which menu items show up
and how much atmosphere (grain, time-of-day warmth, the lights-down effect) you want.

## Building from source

Everything needed to regenerate the skin's colors, fonts and authored artwork lives in `scripts/`:

```
scripts/gen_colors.py          design/tokens.json -> colors/defaults.xml
scripts/make_static_fonts.sh   instances the variable fonts down to the static TTFs Kodi needs
scripts/render_sprites.py      draws the UI chrome (focus ring, buttons, gradients, icons)
scripts/render_defaults.py     draws the Default*.png fallback icons
scripts/render_brand.py        draws resources/icon.png and fanart.jpg
scripts/grade_image.py         grades generated artwork in design/candidates/ into extras/ and media/
scripts/check_skin.py          lints every window file (undefined includes/vars, missing textures, etc.)
scripts/deploy.sh              rsyncs the tree to a Kodi box over SSH and reloads the skin
scripts/package.sh             builds dist/skin.hearthfire-<version>.zip
```

Day-to-day development is `scripts/deploy.sh` against a real device:

```
cp scripts/.deploy.env.example scripts/.deploy.env   # once, then fill in your host details
scripts/deploy.sh
```

Tail the log while you work: `ssh <host> 'tail -f ~/.kodi/temp/kodi.log | grep -iE "skin|error|warning"'`.

## Project layout

```
16x9/            window and include XML (the actual skin)
colors/          generated color palette (do not hand-edit; see design/tokens.json)
fonts/           static TTFs + OFL license files
language/        strings.po, skin-specific IDs in the 31000-31999 range
media/           small UI chrome: sprites, icons, fallback thumbnails
extras/          larger imagery kept outside media/ (backdrops, empty states)
resources/       addon icon, fanart, screenshots
design/          source tokens + the asset ledger consumed by the scripts above
scripts/         everything in the table above
```

## Credits

Fonts: Fraunces, Figtree, Noto Sans, DM Serif Display (SIL Open Font License 1.1, see the license files
shipped alongside each in `fonts/`).

Imagery is generated and then graded to the skin's palette rather than used as-is; the UI chrome, icons and
fallback thumbnails are hand-authored, not generated.

Licensed under CC BY-SA 4.0 — see `LICENSE.txt`.
