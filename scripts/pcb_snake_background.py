"""Add a rounded solder-mask background to a Platane/snk SVG.

snk only supports color_background for GIF output, so the SVG is patched
after generation: a rect covering the viewBox is inserted as the first child.
"""
import re
import sys
from pathlib import Path

MASK = "#0f3d2c"

path = Path(sys.argv[1])
svg = path.read_text(encoding="utf-8")
m = re.search(r"<svg\b[^>]*>", svg)
vb = re.search(r'viewBox="([-\d.\s]+)"', m.group(0))
x, y, w, h = (float(v) for v in vb.group(1).split())
rect = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{MASK}"/>'
path.write_text(svg[: m.end()] + rect + svg[m.end():], encoding="utf-8")
