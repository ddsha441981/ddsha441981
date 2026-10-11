#!/usr/bin/env python3
"""gen_projects.py - builds one 3D slab-card SVG per project + the README table.

Usage:  python gen_projects.py [assets_dir] [readme_snippet.md]
        (defaults: assets/projects  and  projects_table.md)

Edit PROJECTS below, run again, bump ?v= in the README.
Layout: 3 columns. Outer columns tilt inward, the middle sits flat,
so the grid folds toward the centre like an open book (fake perspective).
Pure CSS + SMIL, no JS, GitHub-safe.
"""
import os
import sys
import textwrap
from xml.sax.saxutils import escape

VERSION = 2
CW, CH = 400, 220           # card face
VW, VH = 450, 292           # svg canvas
FX, FY = 25, 22             # card face origin on the canvas
DEPTH_X, DEPTH_Y = 9, 13    # slab thickness (px)
TILT = 2.6                  # degrees of skew (+ left column, - right column)

ORANGE, GREEN, PURPLE, CYAN = "#ff6b00", "#6DB33F", "#a371f7", "#24C8DB"
LOGO = {"Rust": "rust", "Java": "openjdk"}   # shields.io logo slug per language

# slug, emoji, title, description, language chip, highlight chip, accent, repo link, doc link
PROJECTS = [
    ("project-lethe", "🧠", "Project Lethe", "Bio-inspired edge-AI continual-learning engine.",
     "Rust", "4M vec/s", PURPLE, "https://doi.org/10.5281/zenodo.20426838", "docs/projects/project-lethe.md", "paper"),
    ("cl-tds", "⚡", "CL-TDS", "1 MB cache-locked temporal decay sketch.",
     "Rust", "100M+ ops/s", ORANGE, "./assets/projects/docs/cl-tds.md", "docs/projects/cl-tds.md", "repo"),  # repo not public yet; restore https://github.com/ddsha441981/cl-tds when live
    ("wiredoctor", "🩺", "WireDoctor", "Spring Boot context diagnostics & CI gating.",
     "Java", "Tarjan SCC", GREEN, "https://github.com/ddsha441981/wiredoctor", "docs/projects/wiredoctor.md", "repo"),
    ("linefault", "🦀", "LineFault", "Rust cache-line & memory-ordering static analyzer.",
     "Rust", "cache-line", ORANGE, "./assets/projects/docs/linefault.md", "docs/projects/linefault.md", "repo"),  # repo not public yet; restore https://github.com/ddsha441981/linefault when live
    ("pulse-map", "🗺️", "PulseMap", "Fixed-capacity hash map, LFU+LRU eviction.",
     "Rust", "6.5-12x vs moka", ORANGE, "https://github.com/ddsha441981/pulse_map", "docs/projects/pulse-map.md", "repo"),
    ("sketchboot", "🔌", "Sketchboot", "Spring Boot rate limiter via FFM & Rust.",
     "Java", "Java 22 FFM", GREEN, "./assets/projects/docs/sketchboot.md", "docs/projects/sketchboot.md", "repo"),  # repo not public yet; restore https://github.com/ddsha441981/sketchboot when live
    ("struct-mapper", "🧬", "Struct Mapper", "Zero-boilerplate Rust struct derive macro.",
     "Rust", "derive macro", ORANGE, "https://github.com/ddsha441981/struct-mapper", "docs/projects/struct-mapper.md", "repo"),
    ("voxora", "🎙️", "Voxora", "Audio capture & keyring systemd daemon.",
     "Rust", "systemd", ORANGE, "https://github.com/ddsha441981/voxora_service", "docs/projects/voxora.md", "repo"),
    ("godseye", "👁️", "GodsEye", "Tauri 2.0 DWM stealth & VAD engine.",
     "Rust", "Tauri 2.0", CYAN, "https://github.com/ddsha441981/GodseYe_WinX64", "docs/projects/godseye.md", "repo"),
    ("magnetic-math-universe", "🧲", "Math Universe", "Esoteric hardware computation.",
     "Rust", "esoteric ALU", PURPLE, "https://github.com/ddsha441981/MAGNETIC-MATH-UNIVERSE", "docs/projects/magnetic-math-universe.md", "repo"),
]


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(h, other, k):
    a = hex2rgb(h)
    return "#%02x%02x%02x" % tuple(round(a[i] * (1 - k) + other[i] * k) for i in range(3))


def lum(h):
    r, g, b = [v / 255 for v in hex2rgb(h)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def card_svg(idx, slug, emoji, title, desc, lang, metric, acc):
    col = idx % 3                                  # 3-column layout: outer cards fold toward the centre
    tilt = TILT if col == 0 else (-TILT if col == 2 else 0.0)
    sx = -1 if col == 0 else (1 if col == 2 else 0)  # slab thickness on the outer side; middle sits flat
    p = f"c{idx}"
    ink = "#0d1117" if lum(acc) > 0.38 else "#ffffff"
    dark = mix(acc, (0, 0, 0), 0.72)
    mid = mix(acc, (0, 0, 0), 0.5)

    lines = textwrap.wrap(desc, 46)[:2]
    desc_svg = "".join(
        f'<text x="26" y="{116 + i * 21}" class="sans" font-size="14" fill="#aab6c3">{escape(t)}</text>'
        for i, t in enumerate(lines))

    # chips
    lang_w = 30 + len(lang) * 7.4
    met_w = 24 + len(metric) * 7.2
    chips = (
        f'<g transform="translate(26 172)">'
        f'<rect width="{lang_w:.0f}" height="28" rx="14" fill="#0b1018" stroke="{acc}" stroke-opacity="0.55"/>'
        f'<circle cx="15" cy="14" r="4" fill="{acc}"><animate attributeName="opacity" values="1;0.3;1" dur="2.2s" begin="-{idx * 0.37:.2f}s" repeatCount="indefinite"/></circle>'
        f'<text x="26" y="18.5" class="b" font-size="12" fill="#e6edf3">{escape(lang)}</text></g>'
        f'<g transform="translate({26 + lang_w + 10:.0f} 172)">'
        f'<rect width="{met_w:.0f}" height="28" rx="14" fill="{acc}"/>'
        f'<rect width="{met_w:.0f}" height="28" rx="14" fill="url(#{p}hi)"/>'
        f'<text x="{met_w / 2:.0f}" y="18.5" text-anchor="middle" class="b" font-size="12" fill="{ink}">{escape(metric)}</text></g>'
    )

    # slab layers (back to front) give the thickness
    layers = []
    n = 9
    for k in range(n, 0, -1):
        dx, dy = sx * DEPTH_X * k / n, DEPTH_Y * k / n
        shade = mix(dark, (255, 255, 255), 0.0 + 0.06 * (n - k) / n)
        layers.append(f'<rect x="{FX + dx:.1f}" y="{FY + dy:.1f}" width="{CW}" height="{CH}" rx="18" fill="{shade}"/>')
    layers.append(f'<rect x="{FX + sx * DEPTH_X:.1f}" y="{FY + DEPTH_Y:.1f}" width="{CW}" height="{CH}" rx="18" fill="none" stroke="{acc}" stroke-opacity="0.55" stroke-width="1.2"/>')

    cx, cy = FX + CW / 2, FY + CH / 2
    phase = (idx * 0.83) % 5

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {VH}" width="{VW}" height="{VH}" role="img" aria-label="{escape(title)} - {escape(desc)}">
  <title>{escape(title)}</title>
  <defs>
    <style>
      .sans{{font-family:'Segoe UI',system-ui,-apple-system,Arial,sans-serif;}}
      .b{{font-family:'JetBrains Mono',ui-monospace,'Courier New',monospace;font-weight:700;}}
      .e{{font-family:'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji',sans-serif;}}
    </style>
    <linearGradient id="{p}face" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1b2535"/><stop offset="1" stop-color="#0d1320"/></linearGradient>
    <radialGradient id="{p}glow" cx="0.85" cy="0.1" r="0.8"><stop offset="0" stop-color="{acc}" stop-opacity="0.34"/><stop offset="1" stop-color="{acc}" stop-opacity="0"/></radialGradient>
    <linearGradient id="{p}hi" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.35"/><stop offset="1" stop-color="#000" stop-opacity="0.18"/></linearGradient>
    <linearGradient id="{p}shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <linearGradient id="{p}tile" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{mix(acc, (255, 255, 255), 0.25)}"/><stop offset="1" stop-color="{mid}"/></linearGradient>
    <pattern id="{p}scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" fill-opacity="0.035"/></pattern>
    <clipPath id="{p}clip"><rect x="{FX}" y="{FY}" width="{CW}" height="{CH}" rx="18"/></clipPath>
    <filter id="{p}b" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="9"/></filter>
    <filter id="{p}b3" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="3"/></filter>
  </defs>

  <!-- floor shadow + coloured light spill -->
  <ellipse cx="{cx + sx * 6:.0f}" cy="{FY + CH + DEPTH_Y + 14}" rx="{CW * 0.46:.0f}" ry="9" fill="#000" opacity="0.55" filter="url(#{p}b)">
    <animate attributeName="rx" values="{CW * 0.46:.0f};{CW * 0.40:.0f};{CW * 0.46:.0f}" dur="5s" begin="-{phase:.1f}s" repeatCount="indefinite"/></ellipse>
  <ellipse cx="{cx:.0f}" cy="{FY + CH + DEPTH_Y + 12}" rx="{CW * 0.34:.0f}" ry="7" fill="{acc}" opacity="0.28" filter="url(#{p}b)"/>

  <g transform="translate({cx:.1f} {cy:.1f}) skewY({tilt}) scale(0.97 1) translate({-cx:.1f} {-cy:.1f})">
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" dur="5s" begin="-{phase:.1f}s" repeatCount="indefinite"/>
      {"".join(layers)}

      <!-- front face -->
      <rect x="{FX}" y="{FY}" width="{CW}" height="{CH}" rx="18" fill="url(#{p}face)"/>
      <rect x="{FX}" y="{FY}" width="{CW}" height="{CH}" rx="18" fill="url(#{p}glow)"/>
      <rect x="{FX}" y="{FY}" width="{CW}" height="{CH}" rx="18" fill="url(#{p}scan)"/>

      <g clip-path="url(#{p}clip)">
        <!-- faint orbit rings, top-right -->
        <g transform="translate({FX + CW - 62} {FY + 58})" fill="none" stroke="{acc}">
          <circle r="34" stroke-opacity="0.22" stroke-dasharray="3 6"><animateTransform attributeName="transform" type="rotate" values="0;360" dur="26s" repeatCount="indefinite"/></circle>
          <circle r="52" stroke-opacity="0.14" stroke-dasharray="2 9"><animateTransform attributeName="transform" type="rotate" values="360;0" dur="38s" repeatCount="indefinite"/></circle>
          <circle r="70" stroke-opacity="0.09"/>
        </g>
        <!-- light sweep -->
        <g><animateTransform attributeName="transform" type="translate" values="-150 0;-150 0;{CW + 150} 0" keyTimes="0;0.55;1" dur="7s" begin="-{phase + 1:.1f}s" repeatCount="indefinite"/>
          <rect x="{FX - 40}" y="{FY - 10}" width="90" height="{CH + 20}" fill="url(#{p}shine)" transform="skewX(-22)"/></g>
      </g>

      <!-- top-edge highlight + neon border -->
      <path d="M{FX + 18},{FY + 1.5} H{FX + CW - 18}" stroke="#fff" stroke-opacity="0.35" stroke-width="1.2" stroke-linecap="round"/>
      <rect x="{FX}" y="{FY}" width="{CW}" height="{CH}" rx="18" fill="none" stroke="{acc}" stroke-width="3" opacity="0.4" filter="url(#{p}b3)"/>
      <rect x="{FX}" y="{FY}" width="{CW}" height="{CH}" rx="18" fill="none" stroke="{acc}" stroke-opacity="0.8" stroke-width="1.4"/>

      <!-- icon tile (little extruded block) -->
      <g transform="translate({FX + 26} {FY + 26})">
        <rect x="5" y="7" width="58" height="58" rx="15" fill="{dark}"/>
        <rect x="2.5" y="3.5" width="58" height="58" rx="15" fill="{mid}"/>
        <rect width="58" height="58" rx="15" fill="url(#{p}tile)"/>
        <rect width="58" height="58" rx="15" fill="none" stroke="#fff" stroke-opacity="0.45"/>
        <text x="29" y="40" text-anchor="middle" class="e" font-size="30">{emoji}</text>
      </g>

      <!-- title -->
      <text x="{FX + 104}" y="{FY + 50}" class="sans" font-size="22" font-weight="800" fill="#f0f6fc">{escape(title)}</text>
      <rect x="{FX + 104}" y="{FY + 60}" width="{min(150, 18 + len(title) * 9)}" height="3" rx="1.5" fill="{acc}"/>
      <g transform="translate({FX} {FY - 2})">{desc_svg}</g>
      <line x1="{FX + 26}" y1="{FY + 150}" x2="{FX + CW - 26}" y2="{FY + 150}" stroke="#1f2a3a"/>
      <g transform="translate({FX} {FY})">{chips}</g>

      <!-- corner brackets -->
      <path d="M{FX + CW - 40},{FY + 14} H{FX + CW - 14} V{FY + 40}" fill="none" stroke="{acc}" stroke-width="2.2" stroke-linecap="round" opacity="0.9"/>
      <path d="M{FX + CW - 40},{FY + CH - 14} H{FX + CW - 14} V{FY + CH - 40}" fill="none" stroke="{acc}" stroke-width="2.2" stroke-linecap="round" opacity="0.5"/>
    </g>
  </g>
</svg>
'''
    return svg


def shield(s):
    return s.replace("-", "--").replace("_", "__").replace(" ", "%20")


def table_md(items, per_row=3):
    rows = []
    for r in range(0, len(items), per_row):
        imgs = []
        for pr in items[r:r + per_row]:
            slug, emoji, title, desc, lang, metric, acc, link, doc, label = pr
            imgs.append(f'  <a href="./assets/projects/docs/{slug}.md"><img src="./assets/projects/{slug}.svg?v={VERSION}" width="31%" alt="{escape(title)} - {escape(desc)}"/></a>')
        rows.append('<p align="center">\n' + "\n".join(imgs) + '\n</p>')
    chips = "\n".join(
        f'  <a href="{pr[7]}"><img src="https://img.shields.io/badge/{shield(pr[2])}-{pr[6].lstrip("#")}'
        f'?style=flat-square&logo={LOGO.get(pr[4], "github")}&logoColor={"0d1117" if lum(pr[6]) > 0.38 else "ffffff"}" '
        f'alt="{escape(pr[2])} source"/></a>'
        for pr in items)
    rows.append('<p align="center"><sub>source&nbsp;code</sub></p>\n<p align="center">\n' + chips + '\n</p>')
    return ('<!-- Borderless cards (no table = no cell grid). Each card is its own 3D SVG in\n'
            '     assets/projects/ and the whole card links to its deep-dive doc in\n'
            '     assets/projects/docs/<slug>.md. The source chips link each repo/paper,\n'
            '     coloured by the card accent + language logo (shields.io, flat-square).\n'
            '     Edit PROJECTS in tools/gen_projects.py and re-run. -->\n' + "\n".join(rows) + "\n")


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "assets/projects"
    snippet = sys.argv[2] if len(sys.argv) > 2 else "projects_table.md"
    os.makedirs(out_dir, exist_ok=True)
    for i, pr in enumerate(PROJECTS):
        slug, emoji, title, desc, lang, metric, acc = pr[:7]
        with open(os.path.join(out_dir, f"{slug}.svg"), "w", encoding="utf-8") as fh:
            fh.write(card_svg(i, slug, emoji, title, desc, lang, metric, acc))
    with open(snippet, "w", encoding="utf-8") as fh:
        fh.write(table_md(PROJECTS))
    print(f"wrote {len(PROJECTS)} cards to {out_dir} and {snippet}")
