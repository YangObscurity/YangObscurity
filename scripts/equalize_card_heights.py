"""Give side-by-side github-readme-stats cards the same height.

The cards draw their background at height="99%", so raising the root
<svg> height and viewBox of the shorter card extends its background and
the two cards line up top and bottom in the README.
Usage: python scripts/equalize_card_heights.py a.svg b.svg ...
"""
import re
import sys
from pathlib import Path

ROOT = re.compile(r'<svg\b[^>]*>')


def height(svg):
    return float(re.search(r'\bheight="([\d.]+)"', ROOT.search(svg).group(0)).group(1))


def set_height(svg, h):
    tag = ROOT.search(svg).group(0)
    new = re.sub(r'\bheight="[\d.]+"', f'height="{h:g}"', tag, count=1)
    new = re.sub(r'viewBox="([\d.]+) ([\d.]+) ([\d.]+) [\d.]+"',
                 lambda m: f'viewBox="{m.group(1)} {m.group(2)} {m.group(3)} {h:g}"', new, count=1)
    return svg.replace(tag, new, 1)


paths = [Path(p) for p in sys.argv[1:]]
svgs = [p.read_text(encoding="utf-8") for p in paths]
target = max(height(s) for s in svgs)
for p, s in zip(paths, svgs):
    p.write_text(set_height(s, target), encoding="utf-8")
    print(f"{p}: {height(s):g} -> {target:g}")
