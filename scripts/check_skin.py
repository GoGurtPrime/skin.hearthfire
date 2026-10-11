#!/usr/bin/env python3
"""Hearthfire skin lint.

Checks, across 16x9/*.xml:
  [HARD] Every file parses as well-formed XML.
  [HARD] Every $VAR[name], $EXP[name], $CONST[name] reference resolves to a definition somewhere in the skin.
  [HARD] Every <include>Name</include> / <include content="Name"> reference resolves to a named <include> block.
  [HARD] Every static (non-$-expression) texture-like value resolves to a real file under media/ or extras/
         (fallback="..." attributes are checked the same way).
  [WARN] Duplicate control ids within the same window file (excluding template/default controls, which Kodi
         intentionally reuses across dynamically generated rows).
  [WARN] Raw hex color literals outside the small documented utility list (00FFFFFF/00000000/FFFFFFFF and
         short alpha-only overlays like 30FFFFFF/60FFFFFF) - these should be named color tokens instead.
  [WARN] Literal alphabetic label/text content that isn't a digit/symbol and isn't wrapped in $LOCALIZE/$INFO/
         $VAR/$NUMBER/$UPPERCASE (a possible un-localized string).
  [WARN] Windows without a <defaultcontrol> (not all window types need one, so this is advisory only).

Exit code is non-zero only if any HARD check fails.
"""
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIN = ROOT
XML_DIR = SKIN / "16x9"

TEXTURE_TAGS = {
    "texture", "texturefocus", "texturenofocus", "texturebg", "lefttexture", "midtexture", "righttexture",
    "texturesliderbar", "texturesliderbarfocus", "texturenib", "texturenibfocus", "alttexturefocus",
    "alttexturenofocus", "textureup", "texturedown", "texturecheckmark", "textureradiofocus",
    "textureradionofocus", "texturenofocusradioon", "texturefocusradioon", "texturenofocusradiooff",
    "texturefocusradiooff",
}
COLOR_ATTR_TAGS = {
    "textcolor", "focusedcolor", "disabledcolor", "shadowcolor", "colordiffuse",
}
SAFE_HEX = {"00FFFFFF", "00000000", "FFFFFFFF", "30FFFFFF", "60FFFFFF", "50FFFFFF"}

HEX_RE = re.compile(r"^[0-9A-Fa-f]{6}$|^[0-9A-Fa-f]{8}$")
VAR_RE = re.compile(r"\$VAR\[([A-Za-z0-9_]+)")
EXP_RE = re.compile(r"\$EXP\[([A-Za-z0-9_]+)")
CONST_RE = re.compile(r"\$CONST\[([A-Za-z0-9_]+)")
LOCALIZED_TOKEN_RE = re.compile(r"\$(LOCALIZE|INFO|VAR|NUMBER|UPPERCASE|LOWERCASE|CAPITALIZE|EXP|PARAM)\[")

hard_errors: list[str] = []
warnings: list[str] = []


def collect_definitions():
    includes: set[str] = set()
    variables: set[str] = set()
    expressions: set[str] = set()
    constants: set[str] = set()
    files_ok = True
    trees = {}
    for path in sorted(XML_DIR.glob("*.xml")):
        try:
            tree = ET.parse(path)
        except ET.ParseError as e:
            hard_errors.append(f"[XML] {path.name}: not well-formed: {e}")
            files_ok = False
            continue
        trees[path] = tree
        for el in tree.iter("include"):
            name = el.attrib.get("name")
            if name:
                includes.add(name)
        for el in tree.iter("variable"):
            name = el.attrib.get("name")
            if name:
                variables.add(name)
        for el in tree.iter("expression"):
            name = el.attrib.get("name")
            if name:
                expressions.add(name)
        for el in tree.iter("constant"):
            name = el.attrib.get("name")
            if name:
                constants.add(name)
    return trees, includes, variables, expressions, constants, files_ok


INCLUDE_REF_RE = re.compile(r'<include(?:\s+content="([^"]+)")?[^>]*>([^<]*)</include>')


def check_references(trees, includes, variables, expressions, constants):
    for path, tree in trees.items():
        raw = path.read_text(encoding="utf-8")
        for m in VAR_RE.finditer(raw):
            if m.group(1) not in variables:
                hard_errors.append(f"[VAR] {path.name}: $VAR[{m.group(1)}] is not defined anywhere")
        for m in EXP_RE.finditer(raw):
            if m.group(1) not in expressions:
                hard_errors.append(f"[EXP] {path.name}: $EXP[{m.group(1)}] is not defined anywhere")
        for m in CONST_RE.finditer(raw):
            if m.group(1) not in constants:
                hard_errors.append(f"[CONST] {path.name}: $CONST[{m.group(1)}] is not defined anywhere")
        for el in tree.iter("include"):
            content = el.attrib.get("content")
            name = content if content else (el.text.strip() if el.text and el.text.strip() else None)
            if name and name not in includes:
                hard_errors.append(f"[INCLUDE] {path.name}: <include> references undefined name '{name}'")


def resolve_texture_path(value: str) -> bool:
    if "$" in value:
        return True  # dynamic expression, can't statically verify
    if value.startswith("special://skin/"):
        rel = value[len("special://skin/"):]
        return (SKIN / rel).exists()
    for base in (SKIN / "media", SKIN / "extras"):
        if (base / value).exists():
            return True
    return False


def check_textures(trees):
    for path, tree in trees.items():
        for el in tree.iter():
            if el.tag in TEXTURE_TAGS:
                for attr in ("fallback", "background"):
                    val = el.attrib.get(attr)
                    if val and not resolve_texture_path(val):
                        hard_errors.append(f"[TEXTURE] {path.name}: {el.tag}[{attr}]='{val}' not found under media/ or extras/")
                val = (el.text or "").strip()
                if val and not resolve_texture_path(val):
                    hard_errors.append(f"[TEXTURE] {path.name}: <{el.tag}>{val}</{el.tag}> not found under media/ or extras/")


def check_duplicate_ids(trees):
    for path, tree in trees.items():
        seen: dict[str, int] = {}
        root = tree.getroot()
        controls_el = root.find("controls")
        if controls_el is None:
            continue
        for el in controls_el.iter("control"):
            cid = el.attrib.get("id")
            if cid:
                seen[cid] = seen.get(cid, 0) + 1
        dupes = {k: v for k, v in seen.items() if v > 1}
        if dupes:
            warnings.append(f"[DUPID] {path.name}: control id(s) appear more than once at top level: {dupes}")


def check_hardcoded_colors(trees):
    for path, tree in trees.items():
        for el in tree.iter():
            if el.tag in COLOR_ATTR_TAGS or el.tag in TEXTURE_TAGS:
                val = el.attrib.get("colordiffuse") or (el.text if el.tag in COLOR_ATTR_TAGS else None)
                if val and HEX_RE.match(val) and val.upper() not in SAFE_HEX:
                    warnings.append(f"[COLOR] {path.name}: raw hex '{val}' on <{el.tag}> should be a named color token")


def check_literal_strings(trees):
    for path, tree in trees.items():
        for el in tree.iter("label"):
            text = (el.text or "").strip()
            if not text:
                continue
            if LOCALIZED_TOKEN_RE.search(text):
                continue
            if re.fullmatch(r"[0-9+\-\u00b7.]*", text):
                continue
            warnings.append(f"[STRING] {path.name}: literal <label>{text}</label> may need localization")


NO_DEFAULTCONTROL_OK = {
    "DialogBusy.xml", "DialogNotification.xml", "DialogVolumeBar.xml", "DialogExtendedProgressBar.xml",
    "Pointer.xml", "VideoFullScreen.xml", "SlideShow.xml", "Startup.xml", "VideoOSD.xml",
    "Custom_1199_DebugOverlay.xml",
}


def check_defaultcontrol(trees):
    for path, tree in trees.items():
        if path.name in NO_DEFAULTCONTROL_OK:
            continue
        root = tree.getroot()
        if root.tag == "window" and root.find("defaultcontrol") is None:
            warnings.append(f"[DEFAULTCONTROL] {path.name}: no <defaultcontrol> set")


def main() -> int:
    trees, includes, variables, expressions, constants, files_ok = collect_definitions()
    check_references(trees, includes, variables, expressions, constants)
    check_textures(trees)
    check_duplicate_ids(trees)
    check_hardcoded_colors(trees)
    check_literal_strings(trees)
    check_defaultcontrol(trees)

    print(f"Parsed {len(trees)} XML files.")
    print(f"Definitions: {len(includes)} includes, {len(variables)} variables, {len(expressions)} expressions, {len(constants)} constants.\n")

    if warnings:
        print(f"=== {len(warnings)} warning(s) ===")
        for w in warnings:
            print(" ", w)
        print()

    if hard_errors:
        print(f"=== {len(hard_errors)} HARD ERROR(s) ===")
        for e in hard_errors:
            print(" ", e)
        return 1

    print("No hard errors. Lint passed (warnings above, if any, are advisory).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
