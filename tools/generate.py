"""
Generates the profile header for github.com/SAK522 in GitHub's own light and dark colours:
    assets/header-dark.svg, assets/header-light.svg

The header pairs a name block with a small "API response" card — a nod to backend work.
The name is converted to vector outlines from the Inter font (SIL Open Font License), so it
renders identically everywhere; GitHub's image security policy blocks embedded web fonts.
Nothing is hidden behind animation: the only motion is a blinking cursor and status light.

Usage:  pip install fonttools brotli
        python tools/generate.py
"""
import os
from xml.sax.saxutils import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets")
FONT = os.path.join(HERE, "fonts", "inter-latin-700-normal.woff2")
os.makedirs(OUT, exist_ok=True)

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

# ------------------------------------------------------------------ content
NAME = "T. Sakthi"
TITLE = "Backend Developer · Python"
PITCH = "I build REST APIs and data-driven services."
LOCATION = "Tamil Nadu, India"
STATUS = "Open to full-time roles"
REQUEST = ("GET", "/api/v1/engineers/sak522")
RESPONSE = [
    ("{", None),
    ('  "name"', '"T. Sakthi"'),
    ('  "role"', '"Backend Developer"'),
    ('  "stack"', '["Python", "Django", "FastAPI"]'),
    ('  "open_to_work"', "true"),
    ("}", None),
]

# GitHub Primer colours
THEMES = {
    "dark": {
        "bg": "#0d1117", "card": "#161b22", "border": "#30363d", "text": "#e6edf3", "muted": "#9198a1",
        "accent": "#4493f8", "green": "#3fb950", "key": "#79c0ff", "str": "#a5d6ff", "bool": "#ff7b72",
        "punct": "#e6edf3", "rule": "#21262d",
    },
    "light": {
        "bg": "#ffffff", "card": "#f6f8fa", "border": "#d1d9e0", "text": "#1f2328", "muted": "#59636e",
        "accent": "#0969da", "green": "#1a7f37", "key": "#0550ae", "str": "#0a3069", "bool": "#cf222e",
        "punct": "#1f2328", "rule": "#d1d9e0",
    },
}


# ------------------------------------------------------------------ text outlines
class Outliner:
    def __init__(self, path):
        f = TTFont(path)
        self.gs, self.cmap, self.hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
        self.upm = f["head"].unitsPerEm

    def path(self, text, size, x, y, tracking=0.0):
        s = size / self.upm
        pen, cx = SVGPathPen(self.gs), x
        for ch in text:
            g = self.cmap.get(ord(ch))
            if g is None:
                continue
            self.gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
            cx += self.hmtx[g][0] * s + tracking
        return pen.getCommands()


OUTLINE = Outliner(FONT)


def header(theme):
    t = THEMES[theme]
    W, H = 840, 244
    # left column
    lx = 36
    name_path = OUTLINE.path(NAME, 46, lx, 98, tracking=-0.6)

    # right column: API response card
    cx, cy, cw, ch = 436, 24, 380, 196
    mono_y0 = cy + 30
    lines = []
    lines.append(
        f'<text x="{cx + 18}" y="{mono_y0}" class="mono" font-size="12.5">'
        f'<tspan fill="{t["accent"]}" font-weight="700">{REQUEST[0]}</tspan>'
        f'<tspan fill="{t["text"]}"> {escape(REQUEST[1])}</tspan></text>'
    )
    lines.append(
        f'<text x="{cx + 18}" y="{mono_y0 + 20}" class="mono" font-size="12">'
        f'<tspan fill="{t["green"]}" font-weight="700">200 OK</tspan>'
        f'<tspan fill="{t["muted"]}">  ·  application/json</tspan></text>'
    )
    lines.append(f'<line x1="{cx}" y1="{mono_y0 + 33}" x2="{cx + cw}" y2="{mono_y0 + 33}" stroke="{t["rule"]}"/>')
    y = mono_y0 + 55
    for key, val in RESPONSE:
        if val is None:
            lines.append(f'<text x="{cx + 18}" y="{y}" class="mono" font-size="12.5" fill="{t["punct"]}">{key}</text>')
        else:
            vcol = t["bool"] if val in ("true", "false") else t["str"]
            comma = "," if key != '  "open_to_work"' else ""
            lines.append(
                f'<text x="{cx + 18}" y="{y}" class="mono" font-size="12.5" xml:space="preserve">'
                f'<tspan fill="{t["key"]}">{escape(key)}</tspan><tspan fill="{t["punct"]}">: </tspan>'
                f'<tspan fill="{vcol}">{escape(val)}</tspan><tspan fill="{t["punct"]}">{comma}</tspan></text>'
            )
        y += 18.5
    cursor_y = y - 18.5

    body = f"""
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{t['bg']}" stroke="{t['border']}"/>
<path d="{name_path}" fill="{t['text']}"/>
<text x="{lx}" y="132" class="sans" font-size="19" font-weight="600" fill="{t['accent']}">{escape(TITLE)}</text>
<text x="{lx}" y="162" class="sans" font-size="16" fill="{t['text']}">{escape(PITCH)}</text>
<circle cx="{lx + 5}" cy="{195}" r="5" fill="{t['green']}" class="pulse"/>
<text x="{lx + 18}" y="200" class="sans" font-size="14" fill="{t['muted']}"><tspan fill="{t['text']}" font-weight="600">{escape(STATUS)}</tspan>  ·  {escape(LOCATION)}</text>
<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="8" fill="{t['card']}" stroke="{t['border']}"/>
{''.join(lines)}
<rect x="{cx + 32}" y="{cursor_y - 11}" width="7" height="14" fill="{t['muted']}" class="blink"/>
"""
    style = (
        f".sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}"
        ".blink{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
        ".pulse{animation:pulse 2.4s ease-in-out infinite}@keyframes pulse{50%{opacity:.45}}"
        "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
    )
    label = f"{NAME} — {TITLE}. {PITCH} {STATUS}, {LOCATION}."
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="{escape(label)}"><title>{escape(label)}</title><style>{style}</style>{body}</svg>'
    )
    name = f"header-{theme}.svg"
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {name} ({len(svg) / 1024:.1f} KB)")


if __name__ == "__main__":
    header("dark")
    header("light")
