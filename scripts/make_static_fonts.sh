#!/usr/bin/env bash
# Instance the variable fonts (Fraunces, Figtree, Noto Sans) down to the static TTFs Kodi requires,
# and copy them plus their OFL license files into fonts/.
#
# Usage: scripts/make_static_fonts.sh /path/to/downloaded/variable/fonts
#   The source dir must contain:
#     Fraunces-Variable.ttf, Figtree-Variable.ttf, NotoSans-Variable.ttf,
#     DMSerifDisplay-Regular.ttf, DMSerifDisplay-Italic.ttf,
#     OFL-Fraunces.txt, OFL-Figtree.txt, OFL-NotoSans.txt, OFL-DMSerifDisplay.txt
#
# Requires: fonttools (pip install fonttools)
set -euo pipefail

SRC="${1:?Usage: $0 <source-dir-with-variable-fonts>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/fonts"
mkdir -p "$OUT"

FONTTOOLS=(python3 -m fontTools.varLib.instancer)

echo "== Fraunces SemiBold (Display face) =="
"${FONTTOOLS[@]}" -o "$OUT/Fraunces-SemiBold.ttf" "$SRC/Fraunces-Variable.ttf" \
  wght=600 opsz=72 SOFT=50 WONK=0

echo "== Figtree Medium / SemiBold (UI face) =="
"${FONTTOOLS[@]}" -o "$OUT/Figtree-Medium.ttf" "$SRC/Figtree-Variable.ttf" wght=500
"${FONTTOOLS[@]}" -o "$OUT/Figtree-SemiBold.ttf" "$SRC/Figtree-Variable.ttf" wght=600

echo "== Noto Sans Regular (fallback/unicode face) =="
"${FONTTOOLS[@]}" -o "$OUT/NotoSans-Regular.ttf" "$SRC/NotoSans-Variable.ttf" wdth=100 wght=400

echo "== DM Serif Display (static already; italic fallback for taglines) =="
cp "$SRC/DMSerifDisplay-Regular.ttf" "$OUT/DMSerifDisplay-Regular.ttf"
cp "$SRC/DMSerifDisplay-Italic.ttf" "$OUT/DMSerifDisplay-Italic.ttf"

echo "== License files =="
cp "$SRC/OFL-Fraunces.txt" "$OUT/OFL-Fraunces.txt"
cp "$SRC/OFL-Figtree.txt" "$OUT/OFL-Figtree.txt"
cp "$SRC/OFL-NotoSans.txt" "$OUT/OFL-NotoSans.txt"
cp "$SRC/OFL-DMSerifDisplay.txt" "$OUT/OFL-DMSerifDisplay.txt"

echo "Done. Static fonts + licenses written to $OUT"
ls -la "$OUT"
