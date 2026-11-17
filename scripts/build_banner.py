"""Generate assets/banner.svg (PCB workbench banner) and assets/stats-label.svg.

Run from the repository root:  python scripts/build_banner.py
Minimum font size is 18px at the 960px design width (about 15.7px once
GitHub scales the image to the 836px README column).
"""
from pathlib import Path

W, H = 960, 540
NAME = "YangObscurity"

# Palette: solder mask, silkscreen, ENIG gold, copper, LEDs, phosphor screen.
MASK = "#0f3d2c"
MASK_EDGE = "#2a7a57"
SILK = "#f5f7f2"
SILK_DIM = "#b8d8c4"
GOLD = "#e0b341"
COPPER = "#d08a3e"
CHIP = "#141816"
SCREEN = "#06120b"
PHOSPHOR = "#7cffb2"
LED_PWR = "#3fe07a"
LED_TX = "#ffb020"
LED_RX = "#4cc9f0"

# Trace geometry shared by the drawing and the packet animation.
PAD = 10          # edge pad size on module outlines
PKT_INSET = 7     # packet start/end distance from each trace end
TRACE_LEN = (384 - 14) - (64 + 240 + PAD / 2)   # U1 pin end minus J1 pad edge
TRAVEL = TRACE_LEN - 2 * PKT_INSET

MONO = 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace'
SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'

STYLE = f"""
    .mono {{ font-family: {MONO}; }}
    .sans {{ font-family: {SANS}; }}
    @keyframes blink {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: 0.15; }} }}
    @keyframes flow {{ 0% {{ transform: translateX(0); opacity: 0; }} 15% {{ opacity: 1; }} 85% {{ opacity: 1; }} 100% {{ transform: translateX({TRAVEL}px); opacity: 0; }} }}
    @keyframes beat {{ 0%, 100% {{ opacity: 0.25; }} 50% {{ opacity: 1; }} }}
    @keyframes line {{ 0%, 4% {{ opacity: 0; }} 8%, 88% {{ opacity: 1; }} 94%, 100% {{ opacity: 0; }} }}
    .tx {{ animation: blink 0.7s step-end infinite; }}
    .rx {{ animation: blink 0.9s step-end infinite; animation-delay: 0.35s; }}
    .beat {{ animation: beat 1.2s ease-in-out infinite; }}
    .cursor {{ animation: blink 1s step-end infinite; }}
    .pkt {{ animation: flow 1.6s linear infinite; }}
    .ln {{ opacity: 0; animation: line 8s linear infinite; }}
    @media (prefers-reduced-motion: reduce) {{
      .tx, .rx, .beat, .cursor, .pkt, .ln {{ animation: none; opacity: 1; }}
    }}
"""


def text(x, y, s, size=18, fill=SILK, cls="mono", weight=None, anchor=None, extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}"{w}{a}{extra}>{s}</text>'


def module_frame(x, y, w, h, ref, title):
    """Silkscreen outline with a reference designator tab, as on a real board."""
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none" stroke="{SILK}" stroke-width="2" />',
        f'<rect x="{x + 14}" y="{y - 13}" width="{len(ref + title) * 11 + 30}" height="26" fill="{MASK}" />',
        text(x + 22, y + 6, f'<tspan fill="{SILK_DIM}">{ref}</tspan> <tspan fill="{GOLD}" font-weight="700">{title}</tspan>'),
    ])


def build_banner():
    out = []
    # Board outline and mounting holes.
    out.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="{MASK}" stroke="{MASK_EDGE}" stroke-width="2" />')
    for cx, cy in [(30, 30), (W - 30, 30), (30, H - 30), (W - 30, H - 30)]:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="#08110d" stroke="{GOLD}" stroke-width="4" />')

    # Identity.
    out.append(text(64, 98, NAME, 54, SILK, "sans", 700, extra=' letter-spacing="2"'))
    out.append(text(64, 136, "Embedded Systems &#183; IoT Firmware &#183; Backend Telemetry", 20, SILK_DIM))

    # Status LEDs.
    for cx, color, label, cls in [(736, LED_PWR, "PWR", ""), (806, LED_TX, "TX", "tx"), (876, LED_RX, "RX", "rx")]:
        out.append(f'<rect x="{cx - 14}" y="62" width="28" height="14" rx="3" fill="#0a1a12" stroke="{SILK_DIM}" stroke-width="1" />')
        c = f' class="{cls}"' if cls else ""
        out.append(f'<rect{c} x="{cx - 11}" y="65" width="22" height="8" rx="2" fill="{color}" />')
        out.append(text(cx, 106, label, 18, SILK, anchor="middle"))

    out.append(f'<line x1="64" y1="166" x2="{W - 64}" y2="166" stroke="{SILK_DIM}" stroke-width="1.5" stroke-dasharray="8 6" />')

    top, bottom = 206, 470

    # J1: hardware module.
    jx, jw = 64, 240
    out.append(module_frame(jx, top, jw, bottom - top, "J1", "HARDWARE"))
    for i, s in enumerate(["JLC EDA layout", "IP5306 power", "GPRS over UART", "LVGL on ILI9341"]):
        out.append(text(jx + 22, top + 54 + i * 40, s))
    for i in range(8):
        out.append(f'<rect x="{jx + 22 + i * 25}" y="{bottom - 46}" width="16" height="16" rx="2" fill="{GOLD}" />')

    # U1: the MCU.
    cx0, cw = 384, 192
    ctop, cbot = top + 8, bottom - 8
    pins = 9
    step = (cbot - ctop - 40) / (pins - 1)
    pin_ys = [round(ctop + 20 + i * step) for i in range(pins)]
    for py in pin_ys:
        out.append(f'<rect x="{cx0 - 14}" y="{py - 4}" width="14" height="8" fill="{GOLD}" />')
        out.append(f'<rect x="{cx0 + cw}" y="{py - 4}" width="14" height="8" fill="{GOLD}" />')
    out.append(f'<rect x="{cx0}" y="{ctop}" width="{cw}" height="{cbot - ctop}" rx="6" fill="{CHIP}" stroke="#2c332f" stroke-width="2" />')
    out.append(f'<circle class="beat" cx="{cx0 + 20}" cy="{ctop + 20}" r="6" fill="{LED_PWR}" />')
    out.append(text(cx0 + cw - 16, ctop + 26, "U1", 18, SILK_DIM, anchor="end"))
    mid = cx0 + cw / 2
    out.append(text(mid, ctop + 92, "ESP32", 36, SILK, weight=700, anchor="middle"))
    out.append(text(mid, ctop + 134, "ESP-IDF", 18, SILK, anchor="middle"))
    out.append(text(mid, ctop + 164, "FreeRTOS", 18, SILK, anchor="middle"))
    out.append(text(mid, ctop + 194, "C &#183; MicroPython", 18, SILK_DIM, anchor="middle"))

    # U3: backend display.
    dx, dw = 656, 240
    out.append(module_frame(dx, top, dw, bottom - top, "U3", "BACKEND"))
    sx, sy, sw, sh = dx + 14, top + 26, dw - 28, 168
    out.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="4" fill="{SCREEN}" stroke="#2c332f" stroke-width="2" />')
    lines = [("POST /ingest 201", PHOSPHOR), ("GET  /latest 200", PHOSPHOR),
             ("GET  /history 200", PHOSPHOR), ("queue drained", SILK_DIM)]
    for i, (s, col) in enumerate(lines):
        out.append(text(sx + 12, sy + 32 + i * 34, s, 18, col, cls="mono ln", extra=f' style="animation-delay: {i * 1.2}s"'))
    out.append(f'<rect class="cursor" x="{sx + 12}" y="{sy + sh - 22}" width="10" height="16" fill="{PHOSPHOR}" />')
    out.append(text(dx + 22, bottom - 46, "FastAPI", 18))
    out.append(text(dx + 22, bottom - 18, "PostgreSQL", 18))

    # Copper traces with moving packets: J1 -> U1 (I2C), U1 -> U3 (HTTP).
    # Each trace runs from a gold edge pad on the module outline to the outer
    # end of a real U1 pin, on the pin's own centre line.
    trace_ys = pin_ys[3:6]
    for label, edge, x1, x2 in [
        ("I2C", jx + jw, jx + jw + PAD / 2, cx0 - 14),
        ("HTTP", dx, cx0 + cw + 14, dx - PAD / 2),
    ]:
        out.append(text((x1 + x2) / 2, trace_ys[0] - 20, label, 18, SILK, anchor="middle"))
        for k, ty in enumerate(trace_ys):
            out.append(f'<line x1="{x1}" y1="{ty}" x2="{x2}" y2="{ty}" stroke="{COPPER}" stroke-width="4" />')
            out.append(f'<rect x="{edge - PAD / 2}" y="{ty - PAD / 2}" width="{PAD}" height="{PAD}" rx="2" fill="{GOLD}" />')
            out.append(f'<circle class="pkt" cx="{x1 + PKT_INSET}" cy="{ty}" r="5" fill="{SILK}" style="animation-delay: {k * 0.5}s" />')

    # Footer silkscreen.
    out.append(text(64, H - 24, "REV 2026.11", 18, SILK_DIM))
    out.append(text(W - 64, H - 24, "KUALA LUMPUR &#183; MY", 18, SILK_DIM, anchor="end"))

    body = "\n  ".join(out)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="banner-title banner-desc">
  <title id="banner-title">{NAME} - Embedded Systems, IoT Firmware, Backend Telemetry</title>
  <desc id="banner-desc">A circuit board: J1 hardware (JLC EDA layout, IP5306 power, GPRS over UART, LVGL on ILI9341) feeds an ESP32 running ESP-IDF and FreeRTOS, which sends HTTP to a backend display showing FastAPI and PostgreSQL requests.</desc>
  <style>{STYLE}  </style>
  {body}
</svg>
"""


def build_label(label, width):
    """A small PCB-style button used as a details/summary toggle."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="36" viewBox="0 0 {width} 36" role="img" aria-label="{label}">
  <rect x="1" y="1" width="{width - 2}" height="34" rx="6" fill="{MASK}" stroke="{MASK_EDGE}" stroke-width="2" />
  <rect x="12" y="13" width="10" height="10" rx="2" fill="{GOLD}" />
  <text x="32" y="24" font-family='{MONO}' font-size="16" font-weight="700" fill="{SILK}">{label}</text>
</svg>
"""


def char_w(n, size):
    """Approximate monospace advance width."""
    return n * size * 0.61


EMAIL = "yang.obscurity@gmail.com"
ABOUT = ("First-year BSc (Hons) IT student (IoT specialism) at APU, Kuala Lumpur, "
         "working across the full telemetry chain: carrier PCBs in JLC EDA, ESP32 "
         "firmware in ESP-IDF and FreeRTOS, and FastAPI + PostgreSQL ingest services.")
CONTACT = [("LOC", "Kuala Lumpur, MY"), ("MAIL", EMAIL)]
STACK_LABELS = ["LANG", "FIRMWARE", "BACKEND", "HW / OPS"]
STACK = [
    ["C", "Python", "MicroPython", "SQL"],
    ["ESP32", "ESP-IDF", "FreeRTOS", "LVGL", "cJSON"],
    ["FastAPI", "PostgreSQL", "SQLAlchemy", "Pydantic"],
    ["JLC EDA", "Linux", "Docker", "CMake", "Git"],
]

MARGIN = 64        # text margin shared with the banner
HEAD_H = 52        # height of a DS-xx section header band
HEAD_FILL = "#0b3024"


def section_head(y, ref, title, top=False):
    """Darker header band with a reference and title, like a datasheet section."""
    if top:  # first band follows the rounded top corners of the panel
        band = f'<path d="M2 19A17 17 0 0 1 19 2H{W - 19}A17 17 0 0 1 {W - 2} 19V{HEAD_H}H2Z" fill="{HEAD_FILL}" />'
    else:
        band = (f'<rect x="2" y="{y}" width="{W - 4}" height="{HEAD_H}" fill="{HEAD_FILL}" />'
                f'<line x1="2" y1="{y}" x2="{W - 2}" y2="{y}" stroke="{MASK_EDGE}" stroke-width="2" />')
    return "\n  ".join([
        band,
        f'<line x1="2" y1="{y + HEAD_H}" x2="{W - 2}" y2="{y + HEAD_H}" stroke="{MASK_EDGE}" stroke-width="2" />',
        text(MARGIN, y + 33, f'<tspan fill="{SILK_DIM}">{ref}</tspan>  <tspan fill="{GOLD}" font-weight="700">{title}</tspan>'),
    ])


def stack_rows(top, size=18):
    """Skills as SMD chips with gold pins; one row per layer.

    The chip gap is chosen so the widest row ends exactly on the right margin.
    """
    ph, row_h = 40, 60
    x0 = MARGIN + char_w(max(len(l) for l in STACK_LABELS), size) + 40
    widths = [[char_w(len(n), size) + 36 for n in row] for row in STACK]
    gap = min((W - MARGIN - x0 - sum(ws)) / (len(ws) - 1) for ws in widths)
    out = []
    for r, row in enumerate(STACK):
        y = top + r * row_h + (row_h - ph) / 2
        out.append(text(MARGIN, y + ph / 2 + 6, STACK_LABELS[r], size, GOLD, weight=700))
        x = x0
        for name, cw in zip(row, widths[r]):
            n = int((cw - 12) // 18)
            first = x + (cw - (n * 18 - 10)) / 2
            for k in range(n):
                px = first + k * 18
                out.append(f'<rect x="{px:.1f}" y="{y - 5}" width="8" height="5" fill="{GOLD}" />')
                out.append(f'<rect x="{px:.1f}" y="{y + ph}" width="8" height="5" fill="{GOLD}" />')
            out.append(f'<rect x="{x:.1f}" y="{y}" width="{cw:.0f}" height="{ph}" rx="4" fill="{CHIP}" stroke="#2c332f" stroke-width="2" />')
            out.append(text(f"{x + cw / 2:.1f}", y + ph / 2 + 6, name, size, anchor="middle"))
            x += cw + gap
    return out, top + row_h * len(STACK)


def build_datasheet():
    """One panel under the banner: DS-01 description + contact, DS-02 stack.

    Same 960px width as the banner so text scales identically on GitHub.
    """
    import textwrap
    size, lh = 18, 30
    lines = textwrap.wrap(ABOUT, width=int((W - 2 * MARGIN) // char_w(1, size)))
    body_top = HEAD_H + 40
    sep_y = body_top + (len(lines) - 1) * lh + 28
    row_y = sep_y + 40
    head2 = row_y + 30
    rows, rows_end = stack_rows(head2 + HEAD_H + 14)
    h = rows_end + 14

    out = [f'<rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="18" fill="{MASK}" stroke="{MASK_EDGE}" stroke-width="2" />',
           section_head(0, "DS-01", "GENERAL DESCRIPTION", top=True)]
    for i, ln in enumerate(lines):
        out.append(text(MARGIN, body_top + i * lh, ln.replace("&", "&amp;")))
    out.append(f'<line x1="{MARGIN}" y1="{sep_y}" x2="{W - MARGIN}" y2="{sep_y}" stroke="{SILK_DIM}" stroke-width="1.5" stroke-dasharray="8 6" />')
    x = MARGIN
    for key, val in CONTACT:
        out.append(f'<circle cx="{x + 7}" cy="{row_y - 6}" r="7" fill="none" stroke="{GOLD}" stroke-width="3" />')
        out.append(text(x + 24, row_y, f'<tspan fill="{SILK_DIM}">{key}</tspan>  <tspan font-weight="700">{val}</tspan>'))
        x += 24 + char_w(len(key) + 2 + len(val), size) + 56
    out.append(section_head(head2, "DS-02", "TECHNICAL STACK"))
    out += rows

    body = "\n  ".join(out)
    stack_alt = "; ".join(f"{STACK_LABELS[i]}: " + ", ".join(r) for i, r in enumerate(STACK))
    alt = f"{ABOUT} Location: Kuala Lumpur, Malaysia. Email: {EMAIL}. Technical stack. {stack_alt}."
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{alt}">
  <style>.mono {{ font-family: {MONO}; }}</style>
  {body}
</svg>
"""


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent / "assets"
    (root / "banner.svg").write_text(build_banner(), encoding="utf-8")
    (root / "stats-label.svg").write_text(build_label("GITHUB STATS", 170), encoding="utf-8")
    (root / "datasheet.svg").write_text(build_datasheet(), encoding="utf-8")
