#!/usr/bin/env python3
"""gen_connect.py - splits the old connect.svg into a banner + one 3D tile per social.

GitHub shows README SVGs as flat <img>, so links *inside* an SVG never work.
The fix: every tile is its own SVG and the README wraps each one in <a href>.

Usage:  python gen_connect.py [photo_source.svg] [assets_dir] [readme_snippet.md]
  photo_source.svg : an SVG that already holds your embedded portrait (the old
                     connect.svg, or id-dashboard.svg). Default: assets/connect.svg
  defaults         : assets   and   connect_section.md

Writes BOTH themes: <slug>.svg / connect-header.svg (dark, unchanged) and the same names
with a -light suffix. The README snippet wraps each tile in <a><picture>, so the link keeps
working in both themes.

Edit LINKS below, run again, bump ?v= in the README.
Pure CSS + SMIL, no JavaScript, GitHub-safe.
"""
import os
import re
import sys
from xml.sax.saxutils import escape

VERSION = 3
TW, TH = 216, 96            # tile face
VW, VH = 252, 148           # tile canvas
FX, FY = 20, 16
DX, DY = 6, 10              # slab thickness
TILT = 2.2

# slug, label, handle line(s), href, icon text, icon bg, icon fg, accent, icon font-size
LINKS = [
    ("github", "GitHub", ["@ddsha441981"], "https://github.com/ddsha441981", "GH", "#f0f6fc", "#0d1117", "#c9d1d9", 14),
    ("linkedin", "LinkedIn", ["deendayal-kumawat"], "https://linkedin.com/in/deendayal-kumawat", "in", "#0A66C2", "#ffffff", "#2f8cf0", 15),
    ("x", "X / Twitter", ["@ddsha44198"], "https://x.com/ddsha44198", "X", "#000000", "#ffffff", "#9aa7b4", 15),
    ("email", "Email", ["deendayal_kumawat", "@outlook.com"], "mailto:deendayal_kumawat@outlook.com", "@", "#0078D4", "#ffffff", "#2fa4ff", 19),
    ("devto", "dev.to", ["@ddsha441981"], "https://dev.to/ddsha441981", "DEV", "#f0f6fc", "#0d1117", "#b8c4d0", 11),
    ("medium", "Medium", ["@ddsha441981"], "https://medium.com/@ddsha441981", "M", "#f0f6fc", "#0d1117", "#cfd8e0", 17),
    ("crates", "Crates.io", ["/users/ddsha441981"], "https://crates.io/users/ddsha441981", "cr", "#ff6b00", "#0d1117", "#ff6b00", 14),
    ("sponsor", "Sponsor", ["Support the research"], "https://github.com/sponsors/ddsha441981", "♥", "#EA4AAA", "#ffffff", "#EA4AAA", 17),
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


# ---- theme tokens: only colours differ, geometry/animation is identical ----
THEMES = {
    "dark": dict(
        face1="#1b2535", face2="#0d1320", glow_op="0.3",
        shine="#fff", shine_op="0.15", scan="#fff", scan_op="0.035",
        shadow_op="0.55", hi_op="0.35", label="#f0f6fc", handle="#8b98a5",
        slab=lambda acc: mix(acc, (0, 0, 0), 0.74), ramp=(255, 255, 255), ramp_k=0.06,
        # header banner
        h_bg1="#0d1117", h_bg2="#080b11", h_glowL="0.22", h_glowR="0.16", h_lines="0.2",
        h_shadow="0.6", h_accent_txt="#ff6b00", h_title="#e6edf3", h_sub="#aab6c3",
        h_mono="#8b98a5", h_rule="#1f2a3a",
    ),
    "light": dict(
        face1="#ffffff", face2="#edf1f6", glow_op="0.16",
        shine="ACC", shine_op="0.10", scan="#000", scan_op="0.025",
        shadow_op="0.22", hi_op="0.9", label="#1f2328", handle="#57606a",
        slab=lambda acc: mix(acc, (255, 255, 255), 0.5), ramp=(0, 0, 0), ramp_k=0.08,
        h_bg1="#ffffff", h_bg2="#f6f8fa", h_glowL="0.14", h_glowR="0.10", h_lines="0.14",
        h_shadow="0.25", h_accent_txt="#c24f00", h_title="#1f2328", h_sub="#57606a",
        h_mono="#656d76", h_rule="#d0d7de",
    ),
}
# light theme: near-white brand chips would vanish on a white tile, so they flip to dark
LIGHT_ICON_FLIP = {"#f0f6fc": "#1f2328", "#0d1117": "#ffffff"}


def tile_svg(i, slug, label, handle, href, icon, ibg, ifg, acc, ifs, theme="dark"):
    T = THEMES[theme]
    if theme == "light":
        if ibg == "#f0f6fc":                       # GH / DEV / M badges: dark disc, white glyph
            ibg, ifg = LIGHT_ICON_FLIP[ibg], LIGHT_ICON_FLIP[ifg]
        if lum(acc) > 0.6:                         # pale grey accents are invisible on white
            acc = mix(acc, (0, 0, 0), 0.55)
    shine_c = T["shine"].replace("ACC", acc)
    left = i % 4 < 2
    tilt = TILT if left else -TILT
    sx = -1 if left else 1
    p = f"t{i}"
    dark = T["slab"](acc)
    cx, cy = FX + TW / 2, FY + TH / 2
    phase = (i * 0.9) % 5

    layers = []
    n = 7
    for k in range(n, 0, -1):
        dx, dy = sx * DX * k / n, DY * k / n
        shade = mix(dark, T["ramp"], T["ramp_k"] * (n - k) / n)
        layers.append(f'<rect x="{FX + dx:.1f}" y="{FY + dy:.1f}" width="{TW}" height="{TH}" rx="16" fill="{shade}"/>')
    layers.append(f'<rect x="{FX + sx * DX:.1f}" y="{FY + DY:.1f}" width="{TW}" height="{TH}" rx="16" fill="none" stroke="{acc}" stroke-opacity="0.5" stroke-width="1.1"/>')

    hand = "".join(
        f'<text x="{FX + 70}" y="{FY + 57 + j * 15}" class="mono" font-size="11" fill="{T["handle"]}">{escape(t)}</text>'
        for j, t in enumerate(handle))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {VH}" width="{VW}" height="{VH}" role="img" aria-label="{escape(label)}">
  <title>{escape(label)}</title>
  <defs>
    <style>
      .sans{{font-family:'Segoe UI',system-ui,-apple-system,Arial,sans-serif;}}
      .mono{{font-family:'JetBrains Mono','Fira Code',ui-monospace,'Courier New',monospace;}}
    </style>
    <linearGradient id="{p}f" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T["face1"]}"/><stop offset="1" stop-color="{T["face2"]}"/></linearGradient>
    <radialGradient id="{p}g" cx="0.12" cy="0.5" r="0.9"><stop offset="0" stop-color="{acc}" stop-opacity="{T["glow_op"]}"/><stop offset="1" stop-color="{acc}" stop-opacity="0"/></radialGradient>
    <linearGradient id="{p}s" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{shine_c}" stop-opacity="0"/><stop offset="0.5" stop-color="{shine_c}" stop-opacity="{T["shine_op"]}"/><stop offset="1" stop-color="{shine_c}" stop-opacity="0"/></linearGradient>
    <pattern id="{p}sc" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="{T["scan"]}" fill-opacity="{T["scan_op"]}"/></pattern>
    <clipPath id="{p}c"><rect x="{FX}" y="{FY}" width="{TW}" height="{TH}" rx="16"/></clipPath>
    <filter id="{p}b" x="-40%" y="-100%" width="180%" height="300%"><feGaussianBlur stdDeviation="8"/></filter>
    <filter id="{p}b3" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3"/></filter>
  </defs>

  <ellipse cx="{cx + sx * 5:.0f}" cy="{FY + TH + DY + 12}" rx="{TW * 0.44:.0f}" ry="7" fill="#000" opacity="{T["shadow_op"]}" filter="url(#{p}b)"/>
  <ellipse cx="{cx:.0f}" cy="{FY + TH + DY + 10}" rx="{TW * 0.3:.0f}" ry="5" fill="{acc}" opacity="0.25" filter="url(#{p}b)"/>

  <g transform="translate({cx:.1f} {cy:.1f}) skewY({tilt}) translate({-cx:.1f} {-cy:.1f})">
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" dur="4.6s" begin="-{phase:.1f}s" repeatCount="indefinite"/>
      {"".join(layers)}
      <rect x="{FX}" y="{FY}" width="{TW}" height="{TH}" rx="16" fill="url(#{p}f)"/>
      <rect x="{FX}" y="{FY}" width="{TW}" height="{TH}" rx="16" fill="url(#{p}g)"/>
      <rect x="{FX}" y="{FY}" width="{TW}" height="{TH}" rx="16" fill="url(#{p}sc)"/>
      <g clip-path="url(#{p}c)"><g>
        <animateTransform attributeName="transform" type="translate" values="-120 0;-120 0;{TW + 120} 0" keyTimes="0;0.55;1" dur="6.5s" begin="-{phase + 1:.1f}s" repeatCount="indefinite"/>
        <rect x="{FX - 30}" y="{FY - 8}" width="60" height="{TH + 16}" fill="url(#{p}s)" transform="skewX(-22)"/></g></g>
      <path d="M{FX + 16},{FY + 1.4} H{FX + TW - 16}" stroke="#fff" stroke-opacity="{T["hi_op"]}" stroke-width="1.2" stroke-linecap="round"/>
      <rect x="{FX}" y="{FY}" width="{TW}" height="{TH}" rx="16" fill="none" stroke="{acc}" stroke-width="3" opacity="0.38" filter="url(#{p}b3)"/>
      <rect x="{FX}" y="{FY}" width="{TW}" height="{TH}" rx="16" fill="none" stroke="{acc}" stroke-opacity="0.8" stroke-width="1.3"/>

      <circle cx="{FX + 36}" cy="{FY + 49}" r="26" fill="{acc}" opacity="0.28" filter="url(#{p}b3)"/>
      <circle cx="{FX + 36}" cy="{FY + 48}" r="21" fill="{ibg}" stroke="#fff" stroke-opacity="0.4"/>
      <circle cx="{FX + 36}" cy="{FY + 48}" r="21" fill="none" stroke="#fff" stroke-opacity="0.18" stroke-width="5" stroke-dasharray="2 130" transform="rotate(-140 {FX + 36} {FY + 48})"/>
      <text x="{FX + 36}" y="{FY + 48 + ifs * 0.36:.1f}" text-anchor="middle" class="sans" font-size="{ifs}" font-weight="800" fill="{ifg}">{escape(icon)}</text>

      <text x="{FX + 70}" y="{FY + 38}" class="sans" font-size="16.5" font-weight="800" fill="{T["label"]}">{escape(label)}</text>
      {hand}

      <g transform="translate({FX + TW - 30} {FY + 14})" fill="none" stroke="{acc}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <animateTransform attributeName="transform" type="translate" values="{FX + TW - 30} {FY + 14};{FX + TW - 26} {FY + 10};{FX + TW - 30} {FY + 14}" dur="1.6s" begin="-{phase / 2:.1f}s" repeatCount="indefinite"/>
        <path d="M2,14 L14,2 M4,2 H14 V12"/></g>
    </g>
  </g>
</svg>
'''


def header_svg(photo_b64, theme="dark"):
    T = THEMES[theme]
    W, H = 1000, 270
    if theme == "dark":
        hslab = lambda k: mix("#ff6b00", (0, 0, 0), 0.8 - 0.05 * (8 - k) / 8)
    else:
        hslab = lambda k: mix("#ff6b00", (255, 255, 255), 0.5 + 0.02 * (8 - k) / 8)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Let's build something fast - Deendayal Kumawat, Rust systems engineer, Java backend developer, AI researcher">
  <title>Connect</title>
  <defs>
    <style>
      .mono{{font-family:'JetBrains Mono','Fira Code',ui-monospace,'Courier New',monospace;}}
      .sans{{font-family:'Segoe UI',system-ui,-apple-system,Arial,sans-serif;}}
    </style>
    <linearGradient id="hBg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T["h_bg1"]}"/><stop offset="1" stop-color="{T["h_bg2"]}"/></linearGradient>
    <radialGradient id="hGlowL" cx="0.16" cy="0.5" r="0.5"><stop offset="0" stop-color="#ff6b00" stop-opacity="{T["h_glowL"]}"/><stop offset="1" stop-color="#ff6b00" stop-opacity="0"/></radialGradient>
    <radialGradient id="hGlowR" cx="0.85" cy="0.3" r="0.5"><stop offset="0" stop-color="#2f81f7" stop-opacity="{T["h_glowR"]}"/><stop offset="1" stop-color="#2f81f7" stop-opacity="0"/></radialGradient>
    <linearGradient id="hFloor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="0.8"/></linearGradient>
    <mask id="hMask"><rect x="0" y="120" width="1000" height="150" fill="url(#hFloor)"/></mask>
    <clipPath id="hPhoto"><rect x="70" y="30" width="156" height="187" rx="16"/></clipPath>
    <clipPath id="hPanel"><rect width="{W}" height="{H}" rx="20"/></clipPath>
    <filter id="hb" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
    <filter id="hb3" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3"/></filter>
  </defs>

  <rect width="{W}" height="{H}" rx="20" fill="url(#hBg)"/>
  <rect width="{W}" height="{H}" rx="20" fill="url(#hGlowL)"/>
  <rect width="{W}" height="{H}" rx="20" fill="url(#hGlowR)"/>
  <g mask="url(#hMask)" clip-path="url(#hPanel)"><path d="{"".join(f"M0,{c}L1000,{c + 500}M0,{c + 500}L1000,{c}" for c in range(-500, 300, 40))}" stroke="#2f81f7" stroke-opacity="{T["h_lines"]}" fill="none"/></g>

  <!-- signal rings -->
  <g clip-path="url(#hPanel)" fill="none" stroke="#ff6b00">
    <circle cx="148" cy="124" r="100" stroke-width="1.5"><animate attributeName="r" values="100;230" dur="4.5s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.5;0" dur="4.5s" repeatCount="indefinite"/></circle>
    <circle cx="148" cy="124" r="100" stroke-width="1.5"><animate attributeName="r" values="100;230" dur="4.5s" begin="-1.5s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.5;0" dur="4.5s" begin="-1.5s" repeatCount="indefinite"/></circle>
    <circle cx="148" cy="124" r="100" stroke-width="1.5"><animate attributeName="r" values="100;230" dur="4.5s" begin="-3s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.5;0" dur="4.5s" begin="-3s" repeatCount="indefinite"/></circle>
  </g>

  <!-- portrait slab -->
  <ellipse cx="146" cy="236" rx="78" ry="9" fill="#000" opacity="{T["h_shadow"]}" filter="url(#hb)"/>
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" dur="5s" repeatCount="indefinite"/>
    {"".join(f'<rect x="{70 - 8 * k / 8:.1f}" y="{30 + 12 * k / 8:.1f}" width="156" height="187" rx="16" fill="{hslab(k)}"/>' for k in range(8, 0, -1))}
    <rect x="62" y="42" width="156" height="187" rx="16" fill="none" stroke="#ff6b00" stroke-opacity="0.5"/>
    <rect x="70" y="30" width="156" height="187" rx="16" fill="#0e1420"/>
    <image x="70" y="30" width="156" height="187" clip-path="url(#hPhoto)" preserveAspectRatio="xMidYMin slice" xlink:href="data:image/jpeg;base64,{photo_b64}"/>
    <rect x="70" y="30" width="156" height="187" rx="16" fill="none" stroke="#ff6b00" stroke-width="3" opacity="0.45" filter="url(#hb3)"/>
    <rect x="70" y="30" width="156" height="187" rx="16" fill="none" stroke="#ff6b00" stroke-width="2" opacity="0.9"/>
  </g>
  <text x="146" y="258" text-anchor="middle" class="mono" font-size="11" fill="{T["h_mono"]}">Deendayal Kumawat</text>

  <!-- copy -->
  <text x="300" y="82" class="mono" font-size="13" fill="{T["h_accent_txt"]}">// connect --all</text>
  <text x="300" y="128" class="sans" font-size="38" font-weight="800" fill="{T["h_title"]}">Let's Build Something Fast</text>
  <rect x="302" y="142" width="150" height="3" rx="1.5" fill="#ff6b00"/>
  <text x="300" y="174" class="sans" font-size="15.5" fill="{T["h_sub"]}">Rust systems engineer · Java backend developer · AI researcher</text>

  <!-- pick a channel -->
  <g transform="translate(300 218)">
    <text x="0" y="0" class="mono" font-size="12" fill="{T["h_mono"]}">pick a channel</text>
    <g fill="none" stroke="#ff6b00" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
      <path d="M118,-9 L124,-3 L130,-9"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.5s" repeatCount="indefinite"/></path>
      <path d="M134,-9 L140,-3 L146,-9"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.5s" begin="0.25s" repeatCount="indefinite"/></path>
      <path d="M150,-9 L156,-3 L162,-9"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.5s" begin="0.5s" repeatCount="indefinite"/></path>
    </g>
  </g>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="19" fill="none" stroke="{T["h_rule"]}" stroke-width="1.5"/>
</svg>
'''


def mix_hex(*a):
    return mix(*a)


def section_md():
    rows = []
    for r in range(0, len(LINKS), 4):
        imgs = []
        for (slug, label, handle, href, *_rest) in LINKS[r:r + 4]:
            alt = f'{label} - {"".join(handle) if slug == "email" else " ".join(handle)}'
            imgs.append(
                f'  <a href="{href}"><picture>'
                f'<source media="(prefers-color-scheme: light)" srcset="./assets/connect/{slug}-light.svg?v={VERSION}">'
                f'<img src="./assets/connect/{slug}.svg?v={VERSION}" width="24%" alt="{alt}"/>'
                f'</picture></a>')
        rows.append('<p align="center">\n' + "\n".join(imgs) + "\n</p>")
    head = ('<p align="center">\n'
            '  <a href="https://github.com/ddsha441981"><picture>'
            f'<source media="(prefers-color-scheme: light)" srcset="./assets/connect-header-light.svg?v={VERSION}">'
            f'<img src="./assets/connect-header.svg?v={VERSION}" '
            'alt="Connect with Deendayal - Rust systems engineer, Java backend developer, AI researcher" width="100%" />'
            '</picture></a>\n'
            '</p>')
    note = ('<!-- Each tile is its own SVG in assets/connect/ and sits inside an <a>, so every link is clickable.\n'
            '     Edit LINKS in tools/gen_connect.py and re-run to change them. -->')
    return head + "\n\n" + note + "\n" + "\n".join(rows) + "\n"


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "assets/connect.svg"
    out = sys.argv[2] if len(sys.argv) > 2 else "assets"
    snip = sys.argv[3] if len(sys.argv) > 3 else "connect_section.md"
    text = open(src, encoding="utf-8").read()
    m = re.search(r"data:image/(?:jpeg|png);base64,([A-Za-z0-9+/=]{200,})", text)
    if not m:
        sys.exit("No embedded portrait found in " + src)
    os.makedirs(os.path.join(out, "connect"), exist_ok=True)
    for theme, suffix in (("dark", ""), ("light", "-light")):
        with open(os.path.join(out, f"connect-header{suffix}.svg"), "w", encoding="utf-8") as fh:
            fh.write(header_svg(m.group(1), theme))
        for i, l in enumerate(LINKS):
            with open(os.path.join(out, "connect", f"{l[0]}{suffix}.svg"), "w", encoding="utf-8") as fh:
                fh.write(tile_svg(i, *l[:1], l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[8], theme))
    with open(snip, "w", encoding="utf-8") as fh:
        fh.write(section_md())
    print(f"wrote banner + {len(LINKS)} tiles x 2 themes to {out}/ and {snip}")
