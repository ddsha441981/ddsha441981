#!/usr/bin/env python3
"""Put your photo into id-dashboard.svg.

Usage:  python embed_photo.py my_photo.jpg [id-dashboard.svg]

- crops to the badge slot (200:190), keeping the top of the frame so your face stays in
- shrinks to 400x380 and re-encodes as JPEG so the SVG stays small (GitHub is happier under ~300 KB)
- can be run again with a different photo any time; it swaps what is between the PHOTO markers
Needs Pillow for the crop/resize:  pip install pillow
"""
import base64, io, re, sys

photo = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
svg_path = sys.argv[2] if len(sys.argv) > 2 else "id-dashboard.svg"

try:
    from PIL import Image, ImageOps
    img = ImageOps.exif_transpose(Image.open(photo)).convert("RGB")
    target = 200 / 190
    w, h = img.size
    if w / h > target:                       # too wide: crop the sides evenly
        nw = int(h * target); x0 = (w - nw) // 2; img = img.crop((x0, 0, x0 + nw, h))
    else:                                    # too tall: crop from the bottom, keep the head
        nh = int(w / target); y0 = int((h - nh) * 0.15); img = img.crop((0, y0, w, y0 + nh))
    img = img.resize((400, 380), Image.LANCZOS)
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=85, optimize=True)
    data, mime = buf.getvalue(), "image/jpeg"
except ImportError:
    print("Pillow not found, embedding the file as-is (no crop/resize). pip install pillow is better.")
    data = open(photo, "rb").read()
    mime = "image/png" if photo.lower().endswith(".png") else "image/jpeg"

b64 = base64.b64encode(data).decode()
tag = ('<g id="iAvatar" clip-path="url(#iPhoto)">'
       '<rect x="400" y="214" width="200" height="190" fill="#0b111c"/>'
       f'<image x="400" y="214" width="200" height="190" preserveAspectRatio="xMidYMin slice" '
       f'xlink:href="data:{mime};base64,{b64}"/></g>')

svg = open(svg_path, encoding="utf-8").read()
new, n = re.subn(r"(<!--PHOTO:START-->).*?(<!--PHOTO:END-->)", lambda m: m.group(1) + "\n      " + tag + "\n      " + m.group(2), svg, flags=re.S)
if n != 1:
    sys.exit("PHOTO markers not found in the SVG.")
open(svg_path, "w", encoding="utf-8").write(new)
print(f"done: {svg_path} ({len(new)//1024} KB). Bump ?v= in the README so GitHub refreshes it.")
