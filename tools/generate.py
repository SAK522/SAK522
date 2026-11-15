"""
SAK522 GitHub profile — "brass & circuitry" theme (steampunk x futuristic, kept professional).

Generates the animated SVG panels used by README.md:
    hero.svg, dossier.svg, tech-stack.svg, milestones.svg, footer.svg

Design rules:
  * Graphite panels, brass/copper linework, one cool teal accent.
  * Display lettering (name, monogram) is converted to vector outlines from the
    Chakra Petch font (SIL Open Font License), so it renders identically everywhere —
    GitHub's image security policy blocks embedded web fonts.
  * Animations only ADD motion (gears turning, pulses). Nothing starts hidden, so every
    panel is fully readable even if a viewer pauses or blocks animation.

Usage:  pip install fonttools brotli
        python tools/generate.py [path/to/ChakraPetch-Bold.woff2]
"""
import math
import os
import sys
from xml.sax.saxutils import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets")
os.makedirs(OUT, exist_ok=True)

DEFAULT_FONT = os.path.join(HERE, "fonts", "chakra-petch-latin-700-normal.woff2")
FONT_FILE = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FONT

SANS = "Bahnschrift,'DIN Alternate','Avenir Next','Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','Cascadia Mono',Consolas,'SF Mono',Menlo,'Liberation Mono',monospace"

P = {
    "bg": "#0d1015", "panel": "#11151c", "panel2": "#161b23", "plate": "#1b212b",
    "line": "#2a313b", "brass": "#c9a45c", "brass_l": "#ecd9a6", "copper": "#b87333",
    "teal": "#3fd0c9", "text": "#e6e1d6", "dim": "#8b919a", "grey": "#4a515b",
}
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


# ---------------------------------------------------------------- text outlines
class Outliner:
    def __init__(self, path):
        self.font = TTFont(path)
        self.gs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font["head"].unitsPerEm
        self.hmtx = self.font["hmtx"]

    def width(self, text, size, tracking=0.0):
        s = size / self.upm
        w = sum(self.hmtx[self.cmap[ord(c)]][0] * s + tracking for c in text if ord(c) in self.cmap)
        return w - tracking

    def path(self, text, size, x, y, tracking=0.0):
        """SVG path data for `text` with baseline at y, starting at x."""
        s = size / self.upm
        pen = SVGPathPen(self.gs)
        cx = x
        for c in text:
            g = self.cmap.get(ord(c))
            if g is None:
                continue
            self.gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
            cx += self.hmtx[g][0] * s + tracking
        return pen.getCommands()


OUTLINE = Outliner(FONT_FILE)


# ---------------------------------------------------------------- primitives
def svg(w, h, defs, body, style, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>'
        f"<style>.sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}{style}{REDUCED}</style>"
        f"<defs>{BASE_DEFS}{defs}</defs>{body}</svg>"
    )


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote {name:16s} {len(content) / 1024:5.1f} KB")


BASE_DEFS = f"""
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
  <path d="M24 0H0V24" fill="none" stroke="#ffffff" stroke-opacity="0.028" stroke-width="1"/>
</pattern>
<linearGradient id="brassV" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{P['brass_l']}"/><stop offset="0.55" stop-color="{P['brass']}"/><stop offset="1" stop-color="{P['copper']}"/>
</linearGradient>
<radialGradient id="rivet" cx="35%" cy="35%" r="70%">
  <stop offset="0" stop-color="{P['brass_l']}"/><stop offset="1" stop-color="#6e5524"/>
</radialGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
"""


def frame(w, h):
    """Graphite plate + blueprint grid + brass hairline + corner brackets."""
    b, L = 10, 18
    corners = []
    for (x, y, dx, dy) in [(b, b, 1, 1), (w - b, b, -1, 1), (b, h - b, 1, -1), (w - b, h - b, -1, -1)]:
        corners.append(f'<path d="M{x} {y + dy * L} V{y} H{x + dx * L}" fill="none" stroke="{P["brass"]}" stroke-width="1.6"/>')
    return (
        f'<rect width="{w}" height="{h}" rx="12" fill="{P["panel"]}"/>'
        f'<rect width="{w}" height="{h}" rx="12" fill="url(#grid)"/>'
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="11.5" fill="none" stroke="{P["line"]}"/>'
        f'<rect x="5.5" y="5.5" width="{w - 11}" height="{h - 11}" rx="8" fill="none" stroke="{P["brass"]}" stroke-opacity="0.18"/>'
        + "".join(corners)
    )


def section_title(index, label, x=34, y=42):
    return (
        f'<text x="{x}" y="{y}" class="mono" font-size="12" font-weight="700" fill="{P["brass"]}">{index}</text>'
        f'<text x="{x + 26}" y="{y}" class="mono" font-size="12" font-weight="700" letter-spacing="4" fill="{P["teal"]}">{escape(label)}</text>'
    )


def rivet(x, y, r=2.6):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#rivet)"/>'


def gear(cx, cy, r_out, teeth, depth=None, spokes=5, cls="", stroke=None, sw=1.4, fill=None):
    """Line-art gear centred on (cx, cy)."""
    depth = depth or max(4.0, r_out * 0.12)
    r_root = r_out - depth
    seg = 2 * math.pi / teeth
    pts = []
    for i in range(teeth):
        a = i * seg
        for frac, r in ((0.0, r_root), (0.18, r_out), (0.47, r_out), (0.65, r_root)):
            ang = a + frac * seg
            pts.append(f"{cx + r * math.cos(ang):.2f},{cy + r * math.sin(ang):.2f}")
    stroke = stroke or P["brass"]
    fill = fill or P["panel2"]
    hub = r_root * 0.32
    rim = r_root * 0.78
    sp = "".join(
        f'<line x1="{cx + hub * math.cos(k * 2 * math.pi / spokes):.2f}" y1="{cy + hub * math.sin(k * 2 * math.pi / spokes):.2f}" '
        f'x2="{cx + rim * math.cos(k * 2 * math.pi / spokes):.2f}" y2="{cy + rim * math.sin(k * 2 * math.pi / spokes):.2f}"/>'
        for k in range(spokes)
    )
    return (
        f'<g class="{cls}" style="transform-origin:{cx}px {cy}px" fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round">'
        f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{rim:.2f}" stroke-opacity="0.55"/>'
        f'<g stroke-opacity="0.55">{sp}</g>'
        f'<circle cx="{cx}" cy="{cy}" r="{hub:.2f}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{hub * 0.4:.2f}" fill="{stroke}" stroke="none"/>'
        f"</g>"
    )


def spin_css(name, secs, reverse=False):
    return f".{name}{{animation:spin {secs}s linear infinite{' reverse' if reverse else ''}}}"


SPIN_KEYFRAMES = "@keyframes spin{to{transform:rotate(360deg)}}"
PULSE_KEYFRAMES = "@keyframes pulse{0%,100%{opacity:.35}50%{opacity:1}}"


# ================================================================ 1. HERO
def hero():
    W, H = 840, 260
    # meshing gear train (speeds follow the tooth ratio so they look geared)
    g_big = gear(128, 140, 80, 20, cls="g1", sw=1.6)
    g_small = gear(226, 72, 40, 10, cls="g2")
    g_tiny = gear(207, 214, 30, 8, cls="g3")
    core = (
        f'<circle cx="128" cy="140" r="15" fill="{P["teal"]}" opacity="0.25" filter="url(#glow)" class="pulse"/>'
        f'<circle cx="128" cy="140" r="7" fill="{P["teal"]}"/>'
    )

    name = "T. SAKTHI"
    size, tracking = 66, 4
    nx, ny = 300, 136
    name_path = OUTLINE.path(name, size, nx, ny, tracking)
    name_w = OUTLINE.width(name, size, tracking)

    # instrument ruler under the name
    rx0, rx1, ry = nx, 806, 158
    ticks = []
    for i, x in enumerate(range(rx0, rx1 + 1, 10)):
        long_ = i % 5 == 0
        ticks.append(f'<line x1="{x}" y1="{ry}" x2="{x}" y2="{ry - (8 if long_ else 4)}"/>')

    pill_w = 230
    px = W - 34 - pill_w
    body = f"""
{frame(W, H)}
{g_tiny}{g_small}{g_big}{core}
<text x="{nx}" y="66" class="mono" font-size="12" font-weight="700" letter-spacing="3" fill="{P['teal']}">// BACKEND ENGINEER · CLASS OF 2026</text>
<path d="{name_path}" fill="url(#nameGrad)"/>
<g stroke="{P['brass']}" stroke-opacity="0.55" stroke-width="1">{''.join(ticks)}<line x1="{rx0}" y1="{ry}" x2="{rx1}" y2="{ry}"/></g>
<g class="scan"><rect x="{rx0}" y="{ry - 2}" width="34" height="4" rx="2" fill="{P['teal']}" filter="url(#glow)"/><rect x="{rx0 + 10}" y="{ry - 1}" width="14" height="2" fill="{P['teal']}"/></g>
<text x="{nx}" y="194" class="sans" font-size="19" fill="{P['text']}">Building reliable APIs and data-driven systems.</text>
<text x="{nx}" y="222" class="mono" font-size="12" letter-spacing="2" fill="{P['dim']}">PYTHON · DJANGO · FLASK · FASTAPI · POSTGRESQL</text>
<rect x="{px}" y="24" width="{pill_w}" height="26" rx="13" fill="{P['bg']}" stroke="{P['teal']}" stroke-opacity="0.6"/>
<circle cx="{px + 16}" cy="37" r="4" fill="{P['teal']}" class="pulse"/>
<text x="{px + 28}" y="41.5" class="mono" font-size="11" font-weight="700" letter-spacing="1.5" fill="{P['teal']}">OPEN TO FULL-TIME ROLES</text>
"""
    defs = f"""
<linearGradient id="nameGrad" x1="0" y1="{ny - size * 0.75}" x2="0" y2="{ny}" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{P['brass_l']}"/><stop offset="0.6" stop-color="{P['brass']}"/><stop offset="1" stop-color="{P['copper']}"/>
</linearGradient>"""
    style = (
        SPIN_KEYFRAMES + PULSE_KEYFRAMES
        + spin_css("g1", 40) + spin_css("g2", 20, True) + spin_css("g3", 16, True)
        + ".pulse{animation:pulse 2.6s ease-in-out infinite}"
        + f".scan{{animation:scan 5s ease-in-out infinite alternate}}@keyframes scan{{to{{transform:translateX({rx1 - rx0 - 34}px)}}}}"
    )
    write("hero.svg", svg(W, H, defs, body, style, "T. Sakthi — Backend Engineer. Building reliable APIs and data-driven systems."))
    return name_w


# ================================================================ 2. DOSSIER
def dossier():
    W, H = 840, 352
    cx, cy = 150, 186
    ticks = []
    for i in range(72):
        a = i * 2 * math.pi / 72
        r1 = 84 if i % 6 == 0 else 90
        ticks.append(
            f'<line x1="{cx + r1 * math.cos(a):.2f}" y1="{cy + r1 * math.sin(a):.2f}" '
            f'x2="{cx + 96 * math.cos(a):.2f}" y2="{cy + 96 * math.sin(a):.2f}"/>'
        )
    ring = gear(cx, cy, 112, 44, depth=7, spokes=0, cls="ring", sw=1.2, fill="none")
    mono_size = 60
    mono_w = OUTLINE.width("TS", mono_size, 2)
    monogram = OUTLINE.path("TS", mono_size, cx - mono_w / 2, cy + 20, 2)

    rows = [
        ("ROLE", ["Backend Developer · Python"]),
        ("BASE", ["Tamil Nadu, India"]),
        ("EDUCATION", ["B.E. CSE · UCE Pattukkottai · 2022–2026"]),
        ("EXPERIENCE", ["Backend Intern · Coolman Innovations · 2025"]),
        ("FOCUS", ["REST APIs · Databases · Applied AI (RAG)"]),
        ("STRENGTHS", ["Problem solving · Team collaboration", "Quick learning · Attention to detail", "Time management"]),
    ]
    lx, vx, y0, step = 300, 420, 92, 38
    out = []
    for i, (label, lines) in enumerate(rows):
        y = y0 + i * step
        out.append(f'<text x="{lx}" y="{y}" class="mono" font-size="11" font-weight="700" letter-spacing="2" fill="{P["dim"]}">{label}</text>')
        for j, line in enumerate(lines):
            out.append(f'<text x="{vx}" y="{y + j * 21}" class="sans" font-size="15.5" fill="{P["text"]}">{escape(line)}</text>')
        if i < len(rows) - 1:
            out.append(f'<line x1="{lx}" y1="{y + 15}" x2="{W - 34}" y2="{y + 15}" stroke="{P["line"]}"/>')

    body = f"""
{frame(W, H)}
{section_title('01', 'ENGINEER DOSSIER')}
<line x1="34" y1="56" x2="{W - 34}" y2="56" stroke="{P['line']}"/>
{ring}
<circle cx="{cx}" cy="{cy}" r="98" fill="{P['bg']}" stroke="{P['brass']}" stroke-opacity="0.5"/>
<g stroke="{P['brass']}" stroke-opacity="0.7" stroke-width="1.1">{''.join(ticks)}</g>
<circle cx="{cx}" cy="{cy}" r="78" fill="url(#disc)"/>
<circle cx="{cx}" cy="{cy}" r="78" fill="none" stroke="{P['teal']}" stroke-opacity="0.55" class="pulse"/>
<path d="{monogram}" fill="url(#brassV)"/>
<text x="{cx}" y="{cy + 46}" class="mono" font-size="10" font-weight="700" letter-spacing="3" text-anchor="middle" fill="{P['dim']}">SAK522</text>
{rivet(cx - 104, cy - 104)}{rivet(cx + 104, cy - 104)}{rivet(cx - 104, cy + 104)}{rivet(cx + 104, cy + 104)}
{''.join(out)}
"""
    defs = f"""<radialGradient id="disc" cx="50%" cy="40%" r="65%"><stop offset="0" stop-color="#1e2530"/><stop offset="1" stop-color="{P['bg']}"/></radialGradient>"""
    style = SPIN_KEYFRAMES + PULSE_KEYFRAMES + spin_css("ring", 90) + ".pulse{animation:pulse 3s ease-in-out infinite}"
    write("dossier.svg", svg(W, H, defs, body, style,
          "Engineer dossier: Backend Developer (Python), Tamil Nadu, India. B.E. Computer Science, UCE Pattukkottai 2022–2026. Backend Developer Intern, Coolman Innovations 2025."))


# ================================================================ 3. TECH STACK
OK, CAL, Q = "ok", "cal", "q"
MODULES = [
    ("M-01", "CORE & TOOLS", [("Python", OK), ("Java", OK), ("Git", OK), ("pytest", OK), ("Docker", CAL), ("Cloud Deploy", CAL)]),
    ("M-02", "BACKEND", [("Django", OK), ("Flask", OK), ("FastAPI", OK), ("REST APIs", OK), ("JWT Auth", OK)]),
    ("M-03", "DATA", [("SQL", OK), ("PostgreSQL", OK), ("SQLAlchemy", OK), ("Data Analytics", OK)]),
    ("M-04", "AI / ML", [("Machine Learning", OK), ("RAG Pipelines", CAL), ("Vector Databases", Q), ("LLM APIs", Q)]),
]


def led(x, y, state):
    if state == OK:
        return (f'<circle cx="{x}" cy="{y}" r="7" fill="{P["teal"]}" opacity="0.3" filter="url(#glow)" class="pulse"/>'
                f'<circle cx="{x}" cy="{y}" r="4" fill="{P["teal"]}"/>')
    if state == CAL:
        return (f'<circle cx="{x}" cy="{y}" r="4.2" fill="none" stroke="{P["brass"]}" stroke-width="1.6"/>'
                f'<path d="M{x} {y - 4.2} A4.2 4.2 0 0 1 {x} {y + 4.2} Z" fill="{P["brass"]}"/>')
    return f'<circle cx="{x}" cy="{y}" r="4.2" fill="none" stroke="{P["grey"]}" stroke-width="1.6"/>'


def tech_stack():
    W, H = 840, 330
    mw, gap, x0, y0, mh = 180, 13.33, 34, 72, 226
    mods = []
    counts = {OK: 0, CAL: 0, Q: 0}
    for i, (idx, title, items) in enumerate(MODULES):
        x = x0 + i * (mw + gap)
        rows = []
        for j, (label, st) in enumerate(items):
            counts[st] += 1
            ry = y0 + 66 + j * 27
            col = P["text"] if st == OK else (P["brass_l"] if st == CAL else P["dim"])
            rows.append(led(x + 20, ry - 4.5, st) + f'<text x="{x + 34}" y="{ry}" class="sans" font-size="14" fill="{col}">{escape(label)}</text>')
        mods.append(f"""
<rect x="{x}" y="{y0}" width="{mw}" height="{mh}" rx="6" fill="{P['panel2']}" stroke="{P['line']}"/>
<rect x="{x}" y="{y0}" width="{mw}" height="42" rx="6" fill="{P['plate']}"/>
<line x1="{x}" y1="{y0 + 42}" x2="{x + mw}" y2="{y0 + 42}" stroke="{P['brass']}" stroke-opacity="0.7"/>
{rivet(x + 9, y0 + 9, 2.2)}{rivet(x + mw - 9, y0 + 9, 2.2)}
<text x="{x + 16}" y="{y0 + 18}" class="mono" font-size="9.5" font-weight="700" letter-spacing="2" fill="{P['teal']}">{idx}</text>
<text x="{x + 16}" y="{y0 + 35}" class="sans" font-size="14" font-weight="700" letter-spacing="1.5" fill="{P['brass']}">{escape(title)}</text>
{''.join(rows)}""")

    items = [(OK, f"OPERATIONAL {counts[OK]}"), (CAL, f"CALIBRATING {counts[CAL]}"), (Q, f"QUEUED {counts[Q]}")]
    char_w = 10.5 * 0.6 + 1.5          # mono advance + letter-spacing
    widths = [14 + len(t) * char_w for _, t in items]
    lx = W - 34 - (sum(widths) + 22 * (len(items) - 1))
    legend = ""
    for (st, t), w in zip(items, widths):
        legend += led(lx + 4, 38, st) + f'<text x="{lx + 14}" y="42" class="mono" font-size="10.5" font-weight="700" letter-spacing="1.5" fill="{P["dim"]}">{t}</text>'
        lx += w + 22
    body = f"""
{frame(W, H)}
{section_title('02', 'TECH STACK')}
{legend}
<line x1="34" y1="56" x2="{W - 34}" y2="56" stroke="{P['line']}"/>
{''.join(mods)}
"""
    style = PULSE_KEYFRAMES + ".pulse{animation:pulse 2.8s ease-in-out infinite}"
    write("tech-stack.svg", svg(W, H, "", body, style,
          "Tech stack. Operational: Python, Java, Git, pytest, Django, Flask, FastAPI, REST APIs, JWT Auth, SQL, PostgreSQL, SQLAlchemy, Data Analytics, Machine Learning. Calibrating: Docker, Cloud Deploy, RAG Pipelines. Queued: Vector Databases, LLM APIs."))


# ================================================================ 4. MILESTONES
MILESTONES = [
    (True, "2022", "Started B.E. CSE", "UCE Pattukkottai"),
    (True, "2025", "Backend Internship", "Coolman Innovations"),
    (True, "B.E. PROJECT", "Smart Agriculture DSS", "Applied machine learning"),
    (True, "2026", "B.E. CSE Graduate", "Class of 2026"),
    (True, "2026", "Expense Tracker API", "FastAPI · JWT · 20/20 tests"),
    (False, "NEXT", "Production Deploy", "Expense Tracker goes live"),
    (False, "NEXT", "Document Q&A API", "RAG · embeddings · LLMs"),
]


def milestones():
    W, H = 840, 270
    xs = [62 + i * 119.3 for i in range(len(MILESTONES))]
    rail_y = 152
    last_done = max(i for i, m in enumerate(MILESTONES) if m[0])
    parts = []
    for i, ((done, year, title, sub), x) in enumerate(zip(MILESTONES, xs)):
        above = i % 2 == 0
        anchor = "start" if i == 0 else ("end" if i == len(MILESTONES) - 1 else "middle")
        tx = x - 8 if anchor == "start" else (x + 8 if anchor == "end" else x)
        ycol = P["teal"] if not done else P["brass"]
        if above:
            yy, ty, sy, c1, c2 = 84, 106, 124, rail_y - 12, 132
        else:
            yy, ty, sy, c1, c2 = 196, 218, 236, rail_y + 12, 182
        parts.append(f'<line x1="{x:.1f}" y1="{c1}" x2="{x:.1f}" y2="{c2}" stroke="{P["brass"]}" stroke-opacity="0.4"/>')
        if done:
            parts.append(f'<circle cx="{x:.1f}" cy="{rail_y}" r="9" fill="{P["plate"]}" stroke="{P["brass"]}" stroke-width="2"/>'
                         f'<circle cx="{x:.1f}" cy="{rail_y}" r="3.5" fill="url(#brassV)"/>')
        else:
            parts.append(f'<circle cx="{x:.1f}" cy="{rail_y}" r="13" fill="{P["teal"]}" opacity="0.25" filter="url(#glow)" class="pulse"/>'
                         f'<circle cx="{x:.1f}" cy="{rail_y}" r="9" fill="{P["bg"]}" stroke="{P["teal"]}" stroke-width="2" stroke-dasharray="3 3"/>')
        parts.append(
            f'<text x="{tx:.1f}" y="{yy}" class="mono" font-size="10.5" font-weight="700" letter-spacing="2" text-anchor="{anchor}" fill="{ycol}">{escape(year)}</text>'
            f'<text x="{tx:.1f}" y="{ty}" class="sans" font-size="15" font-weight="700" text-anchor="{anchor}" fill="{P["text"] if done else P["brass_l"]}">{escape(title)}</text>'
            f'<text x="{tx:.1f}" y="{sy}" class="mono" font-size="10.5" text-anchor="{anchor}" fill="{P["dim"]}">{escape(sub)}</text>'
        )
    xd = xs[last_done]
    body = f"""
{frame(W, H)}
{section_title('03', 'MILESTONES')}
<text x="{W - 34}" y="42" class="mono" font-size="10.5" font-weight="700" letter-spacing="1.5" text-anchor="end" fill="{P['dim']}">{sum(m[0] for m in MILESTONES)} COMPLETE · {sum(not m[0] for m in MILESTONES)} IN QUEUE</text>
<line x1="34" y1="56" x2="{W - 34}" y2="56" stroke="{P['line']}"/>
<line x1="{xs[0]:.1f}" y1="{rail_y}" x2="{xd:.1f}" y2="{rail_y}" stroke="url(#railGrad)" stroke-width="3"/>
<line x1="{xd:.1f}" y1="{rail_y}" x2="{xs[-1]:.1f}" y2="{rail_y}" stroke="{P['teal']}" stroke-opacity="0.6" stroke-width="2" stroke-dasharray="6 6" class="flow"/>
<g class="spark"><circle cx="{xs[0]:.1f}" cy="{rail_y}" r="5" fill="{P['teal']}" filter="url(#glow)"/><circle cx="{xs[0]:.1f}" cy="{rail_y}" r="2" fill="#ffffff"/></g>
{''.join(parts)}
"""
    defs = f"""<linearGradient id="railGrad" x1="{xs[0]:.1f}" y1="0" x2="{xd:.1f}" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{P['copper']}"/><stop offset="1" stop-color="{P['brass_l']}"/></linearGradient>"""
    style = (
        PULSE_KEYFRAMES + ".pulse{animation:pulse 2.4s ease-in-out infinite}"
        + ".flow{animation:flow 1.4s linear infinite}@keyframes flow{to{stroke-dashoffset:-24}}"
        + f".spark{{animation:spark 4.5s ease-in-out infinite}}@keyframes spark{{0%{{transform:translateX(0);opacity:0}}10%{{opacity:1}}90%{{opacity:1}}100%{{transform:translateX({xd - xs[0]:.1f}px);opacity:0}}}}"
    )
    write("milestones.svg", svg(W, H, defs, body, style,
          "Milestones: started B.E. CSE 2022; backend internship at Coolman Innovations 2025; Smart Agriculture ML project; graduated 2026; built Expense Tracker API. Next: production deploy and a RAG document Q&A API."))


# ================================================================ 5. FOOTER
def footer():
    W, H = 840, 84
    body = f"""
{frame(W, H)}
{gear(52, 42, 20, 9, cls="g1", sw=1.2)}
{gear(84, 30, 12, 6, cls="g2", sw=1.1)}
<text x="{W / 2}" y="47" class="mono" font-size="11.5" font-weight="700" letter-spacing="4" text-anchor="middle" fill="{P['dim']}">END OF TRANSMISSION · THANKS FOR VISITING</text>
<text x="{W - 34}" y="47" class="mono" font-size="11" font-weight="700" letter-spacing="2" text-anchor="end" fill="{P['brass']}">SAK522</text>
"""
    style = SPIN_KEYFRAMES + spin_css("g1", 18) + spin_css("g2", 12, True)
    write("footer.svg", svg(W, H, "", body, style, "End of transmission. Thanks for visiting."))


if __name__ == "__main__":
    hero()
    dossier()
    tech_stack()
    milestones()
    footer()
