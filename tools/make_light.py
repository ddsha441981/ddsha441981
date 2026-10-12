#!/usr/bin/env python3
"""make_light.py - derive a light-theme twin (<name>-light.svg) of each hand-made dark SVG.

Usage:  python make_light.py hero.svg about-life.svg stack.svg id-dashboard.svg
        python make_light.py assets/*.svg          (skips files that already end in -light.svg)

Design, geometry, animation and the embedded photo are copied untouched. Only colours change:

  - page / card backgrounds  -> white / GitHub-light greys (gradient stops, per gradient id)
  - surfaces (chips, blocks) -> #f6f8fa / #e8edf3, borders -> #d0d7de / #c2cad4
  - text                     -> #1f2328 (primary) / #57606a / #656d76 (muted)
  - small accent text        -> slightly deeper (orange #c24f00, blue #0969da, green #1a7f37,
                                red #cf222e) so it stays readable on white
  - accent SHAPES (orange bars, blue/green blocks, avatar ring, strap, orbit rings) keep their hue
  - text that sits on a coloured fill (e.g. 'Zig' on yellow, 'DEVELOPER ACCESS' on orange)
    is left alone, as is every <image> and the photo groups (hAvatar / iAvatar)

Anything it did not recognise is printed at the end so nothing slips through silently.
Run it again after you change a dark SVG (or swap the photo with embed_photo.py).
Then bump ?v= in the README.
"""
import re
import sys
import os
import collections

# --- colour maps -------------------------------------------------------------------------
TEXT = {                       # fill on <text> and on <g> that only carries text
    "#e6edf3": "#1f2328",
    "#cdd9e5": "#3b4452",
    "#9fb0c3": "#57606a",
    "#8b98a5": "#656d76",
    "#ff6b00": "#c24f00",
    "#ff8a2b": "#c24f00",
    "#2f81f7": "#0969da",
    "#5a9cff": "#0969da",
    "#3fb950": "#1a7f37",
    "#ff5d5d": "#cf222e",
}
SHAPE = {                      # fill on rect / circle / ellipse / path
    "#111826": "#f6f8fa",
    "#0c121c": "#f6f8fa",
    "#1a2433": "#e8edf3",
    "#1a2130": "#e1e6ec",
}
STROKE = {
    "#1f2a3a": "#d0d7de",
    "#2a3650": "#c2cad4",
}
STOPS = {                      # per gradient id: stop-color remap (ids not listed keep colours)
    "hBg":   {"#0d1117": "#ffffff", "#0b0f16": "#fbfcfd", "#0a0d14": "#f6f8fa"},
    "aBg":   {"#0d1117": "#ffffff", "#0a0d14": "#f6f8fa"},
    "sBg":   {"#0d1117": "#ffffff", "#090c12": "#f6f8fa"},
    "iBg":   {"#0d1117": "#ffffff", "#090c12": "#f6f8fa"},
    "hName": {"#ffffff": "#1f2328", "#ffd9b8": "#9a4208"},      # white -> peach -> orange becomes dark -> brown -> orange
    "hRim":  {"#1b2436": "#ffffff", "#0b0f16": "#e9edf2"},
    "sVign": {"#13203a": "#cfe0fb", "#0a0d14": "#f6f8fa"},
    "iCard": {"#161f30": "#ffffff", "#0e1420": "#eef2f6"},
    "iFoil": {"#ffffff": "#0d1117"},                              # light sweep becomes a faint dark sweep
}
EXTRA_IN_GRADIENT = {"iFoil": [('stop-opacity="0.2"', 'stop-opacity="0.07"')]}

HEX = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")


def attr_map(tag, attr, table):
    def sub(m):
        val = m.group(2)
        return f'{m.group(1)}"{table.get(val.lower(), val)}"'
    return re.sub(rf'(\s{attr}=)"(#[0-9a-fA-F]{{3,6}})"', sub, tag)


def convert(svg):
    # 1. park things that must not be touched: comments, photo groups, <metadata>
    parked = []

    def park(m):
        parked.append(m.group(0))
        return f"\x00{len(parked) - 1}\x00"

    svg = re.sub(r"<metadata>.*?</metadata>", "", svg, flags=re.S)          # C2PA blob is invalid after edits
    svg = svg.replace(' xmlns:c2pa="http://c2pa.org/manifest"', "")
    svg = re.sub(r"<!--.*?-->", park, svg, flags=re.S)
    svg = re.sub(r'<g id="(?:hAvatar|iAvatar)"[^>]*>.*?</g>', park, svg, flags=re.S)
    svg = re.sub(r"<image\b[^>]*/>", park, svg, flags=re.S)

    # 2. gradient stops, per gradient id
    def grad(m):
        gid, body = m.group(2), m.group(0)
        for old, new in STOPS.get(gid, {}).items():
            body = body.replace(f'stop-color="{old}"', f'stop-color="{new}"')
        for old, new in EXTRA_IN_GRADIENT.get(gid, []):
            body = body.replace(old, new)
        return body
    svg = re.sub(r'<(linearGradient|radialGradient) id="([^"]+)".*?</\1>', grad, svg, flags=re.S)

    # 3. element-level fills / strokes
    def tag(m):
        t, name = m.group(0), m.group(1)
        if name in ("text", "g"):
            t = attr_map(t, "fill", TEXT)
        elif name in ("rect", "circle", "ellipse", "path"):
            t = attr_map(t, "fill", SHAPE)
        t = attr_map(t, "stroke", STROKE)
        return t
    svg = re.sub(r"<(text|g|rect|circle|ellipse|path|line)\b[^>]*>", tag, svg)

    # 4. restore parked chunks
    return re.sub(r"\x00(\d+)\x00", lambda m: parked[int(m.group(1))], svg)


def leftovers(svg):
    """colours still present outside parked areas, so you can eyeball anything unmapped"""
    s = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    s = re.sub(r'<g id="(?:hAvatar|iAvatar)"[^>]*>.*?</g>', "", s, flags=re.S)
    s = re.sub(r"data:image/[a-z]+;base64,[A-Za-z0-9+/=]+", "", s)
    return collections.Counter(c.lower() for c in HEX.findall(s))


def main(paths):
    for p in paths:
        if p.endswith("-light.svg") or not p.endswith(".svg"):
            continue
        out = p[:-4] + "-light.svg"
        light = convert(open(p, encoding="utf-8").read())
        open(out, "w", encoding="utf-8").write(light)
        left = leftovers(light)
        print(f"{p} -> {out} ({len(light) // 1024} KB)")
        print("   colours kept as-is:", ", ".join(f"{c} x{n}" for c, n in left.most_common()))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
