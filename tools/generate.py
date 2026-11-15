"""
Generates the animated SVG panels for the SAK522 GitHub profile README.
Retro-arcade theme. All art (pixel font, avatar, coins, icons) is original.
Run:  python generate.py   -> writes SVGs into ../SAK522/assets/
"""
import os
import random
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(OUT, exist_ok=True)

FONT = "'Courier New',ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
C = {
    "bg": "#0b0f1a", "panel": "#0f1626", "cyan": "#00e5ff", "mag": "#ff2fd6",
    "green": "#39ff88", "yellow": "#ffd23f", "gold_d": "#b8860b", "grey": "#4b5563",
    "grey_l": "#6b7280", "text": "#e5e7eb", "dim": "#94a3b8", "red": "#ff4d6d",
}

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"

# ------------------------------------------------------------------ pixel font
GLYPHS = {
    "A": [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "C": [" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "],
    "D": ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "G": [" ### ", "#   #", "#    ", "# ###", "#   #", "#   #", " ####"],
    "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "I": [" ### ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "K": ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    "M": ["#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "S": [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    ".": ["     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "],
    ">": ["#    ", " #   ", "  #  ", "   # ", "  #  ", " #   ", "#    "],
    " ": ["     "] * 7,
}


def pixel_text_width(text, px):
    return len(text) * 6 * px - px


def pixel_text(text, x, y, px, fill, attrs=""):
    """Render text with the 5x7 pixel font; merges horizontal runs into one rect."""
    rects = []
    for ci, ch in enumerate(text.upper()):
        rows = GLYPHS[ch]
        for r, row in enumerate(rows):
            c = 0
            while c < 5:
                if row[c] == "#":
                    start = c
                    while c < 5 and row[c] == "#":
                        c += 1
                    rx = x + (ci * 6 + start) * px
                    rects.append(
                        f'<rect x="{rx:g}" y="{y + r * px:g}" width="{(c - start) * px:g}" height="{px:g}"/>'
                    )
                else:
                    c += 1
    return f'<g fill="{fill}" {attrs}>{"".join(rects)}</g>'


def pixel_sprite(rows, palette, x, y, px):
    rects = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch in palette:
                start = c
                while c < len(row) and row[c] == ch:
                    c += 1
                rects.append(
                    f'<rect x="{x + start * px:g}" y="{y + r * px:g}" width="{(c - start) * px:g}" '
                    f'height="{px:g}" fill="{palette[ch]}"/>'
                )
            else:
                c += 1
    return "".join(rects)


def svg(w, h, body, style, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>'
        f"<style>{style}{REDUCED}</style>{body}</svg>"
    )


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote {name} ({len(content)//1024 + 1} KB)")


COMMON_DEFS = f"""
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
  <rect width="4" height="1" fill="#ffffff" opacity="0.035"/>
</pattern>
<radialGradient id="vig" cx="50%" cy="45%" r="75%">
  <stop offset="60%" stop-color="#000" stop-opacity="0"/>
  <stop offset="100%" stop-color="#000" stop-opacity="0.55"/>
</radialGradient>
<filter id="glow" x="-20%" y="-40%" width="140%" height="180%">
  <feGaussianBlur stdDeviation="4" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="softglow" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="3"/>
</filter>
"""

COIN = ["..XXX..", ".XYYYX.", "XYYXYYX", "XYYXYYX", "XYYXYYX", ".XYYYX.", "..XXX.."]
COIN_PAL = {"X": C["gold_d"], "Y": C["yellow"]}


# ======================================================== 1. TITLE SCREEN
def title_screen():
    W, H = 840, 250
    rnd = random.Random(522)
    stars = []
    for i in range(46):
        sx, sy = rnd.randint(14, W - 14), rnd.randint(14, H - 14)
        size = rnd.choice([2, 2, 2, 3])
        col = rnd.choice([C["text"], C["cyan"], C["mag"], C["text"]])
        delay = rnd.uniform(0, 3)
        dur = rnd.uniform(1.6, 3.4)
        stars.append(
            f'<rect class="star" x="{sx}" y="{sy}" width="{size}" height="{size}" fill="{col}" '
            f'style="animation-delay:{delay:.2f}s;animation-duration:{dur:.2f}s"/>'
        )

    name = "T. SAKTHI"
    px = 9
    tw = pixel_text_width(name, px)
    tx = (W - tw) / 2
    ty = 72
    title = (
        pixel_text(name, tx + 6, ty + 6, px, C["mag"], 'opacity="0.9"')
        + pixel_text(name, tx, ty, px, C["cyan"], 'filter="url(#softglow)" opacity="0.8"')
        + pixel_text(name, tx, ty, px, "url(#tg)")
    )

    coin_l = f'<g class="coin" style="transform-origin:{tx - 50 + 17.5}px {ty + 31}px">' + pixel_sprite(COIN, COIN_PAL, tx - 50, ty + 14, 5) + "</g>"
    coin_r_x = tx + tw + 16
    coin_r = f'<g class="coin" style="transform-origin:{coin_r_x + 17.5}px {ty + 31}px;animation-delay:.6s">' + pixel_sprite(COIN, COIN_PAL, coin_r_x, ty + 14, 5) + "</g>"

    sub = "BACKEND DEVELOPER  ·  PYTHON  ·  DJANGO  ·  FASTAPI  ·  SQL"
    sub_y = 178
    sub_w = 650
    sub_x = (W - sub_w) / 2

    ps = "> PRESS START"
    ps_px = 3
    ps_x = (W - pixel_text_width(ps, ps_px)) / 2

    body = f"""
<defs>{COMMON_DEFS}
<linearGradient id="tg" x1="0" y1="{ty}" x2="0" y2="{ty + 63}" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#d9fdff"/><stop offset="0.5" stop-color="{C['cyan']}"/><stop offset="1" stop-color="#2a8cff"/>
</linearGradient>
<clipPath id="type"><rect x="{sub_x - 6}" y="{sub_y - 20}" height="30" width="{sub_w + 12}">
  <animate attributeName="width" from="0" to="{sub_w + 12}" begin="0.6s" dur="2.8s" fill="freeze"/>
</rect></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{C['bg']}"/>
<g>{''.join(stars)}</g>
<line x1="24" y1="44" x2="{W - 24}" y2="44" stroke="{C['cyan']}" stroke-opacity="0.25"/>
<text x="28" y="32" class="hud" fill="{C['red']}">1UP</text>
<text x="70" y="32" class="hud" fill="{C['text']}">SAK522</text>
<text x="{W / 2}" y="32" class="hud" fill="{C['dim']}" text-anchor="middle">STAGE <tspan fill="{C['yellow']}">2026</tspan></text>
<text x="{W - 28}" y="32" class="hud blink" fill="{C['yellow']}" text-anchor="end">INSERT COIN</text>
{coin_l}{coin_r}
{title}
<g clip-path="url(#type)"><text x="{W / 2}" y="{sub_y}" class="sub" text-anchor="middle" fill="{C['text']}">{escape(sub)}</text></g>
<rect class="cursor" x="{sub_x + sub_w + 4}" y="{sub_y - 15}" width="9" height="18" fill="{C['green']}">
  <animate attributeName="x" from="{sub_x - 6}" to="{sub_x + sub_w + 4}" begin="0.6s" dur="2.8s" fill="freeze"/>
</rect>
<g class="blink2">{pixel_text(ps, ps_x, 206, ps_px, C['green'])}</g>
<rect width="{W}" height="{H}" rx="14" fill="url(#scan)"/>
<rect width="{W}" height="{H}" rx="14" fill="url(#vig)"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="13" fill="none" stroke="{C['cyan']}" stroke-opacity="0.45" stroke-width="2"/>
"""
    style = f"""
.hud{{font:700 14px {FONT};letter-spacing:2px}}
.sub{{font:700 17px {FONT};letter-spacing:1px}}
.star{{animation:tw 2.4s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:1}}}}
.blink{{animation:bl 1.1s steps(1) infinite}}
.blink2{{animation:bl 1.2s steps(1) infinite}}
@keyframes bl{{0%{{opacity:1}}50%{{opacity:0}}}}
.cursor{{animation:bl .8s steps(1) infinite}}
.coin{{animation:spin 1.8s ease-in-out infinite}}
@keyframes spin{{0%,100%{{transform:scaleX(1)}}50%{{transform:scaleX(.15)}}}}
"""
    write("title-screen.svg", svg(W, H, body, style, "T. SAKTHI - Backend Developer - Press Start"))


# ======================================================== 2. PLAYER CARD
AVATAR = [
    "................",
    "....PPPPPPPP....",
    "...PKKKKKKKKP...",
    "..PKKKKKKKKKKP..",
    "..PKKSSSSSSKKP..",
    "..PSSSSSSSSSSP..",
    ".PPSGGGSSGGGSPP.",
    ".PPSGEGSSGEGSPP.",
    "..PSGGGSSGGGSP..",
    "...SSSSssSSSS...",
    "....SSSMMSSS....",
    ".....SSSSSS.....",
    "....HHHssHHH....",
    "..HHHHHCCHHHHH..",
    ".HHHHHCHHCHHHHH.",
    "HHHHHHHHHHHHHHHH",
]
AV_PAL = {
    "K": "#2a1d18", "S": "#b97a50", "s": "#8f5a36", "G": C["cyan"], "E": "#0b0f1a",
    "M": "#6b2f1f", "P": C["mag"], "H": "#3b4fd8", "C": C["text"],
}


def player_card():
    W, H = 840, 350
    px = 11
    ax, ay = 36 + 7, 70 + 7
    avatar = pixel_sprite(AVATAR, AV_PAL, ax, ay, px)
    # eyelids for blinking (skin over the pupils)
    lids = (
        f'<rect x="{ax + 5 * px}" y="{ay + 7 * px}" width="{px}" height="{px}" fill="{AV_PAL["S"]}"/>'
        f'<rect x="{ax + 10 * px}" y="{ay + 7 * px}" width="{px}" height="{px}" fill="{AV_PAL["S"]}"/>'
    )

    rows = [
        ("NAME", "T. Sakthi"),
        ("CLASS", "Backend Developer"),
        ("ORIGIN", "Tamil Nadu, India"),
        ("GUILD", "B.E. CSE · UCE Pattukkottai '22–'26"),
        ("EXP", "Backend Intern @ Coolman Innovations '25"),
    ]
    info = []
    for i, (k, v) in enumerate(rows):
        y = 92 + i * 29
        label = (k + " ").ljust(10, ".")
        info.append(
            f'<text x="262" y="{y}" class="row"><tspan fill="{C["dim"]}">{escape(label)} </tspan>'
            f'<tspan fill="{C["text"]}">{escape(v)}</tspan></text>'
        )

    bar_x, bar_y, bar_w, bar_h = 262, 256, 540, 18
    fill_w = round(bar_w * 0.68)
    segs = "".join(
        f'<rect x="{bar_x + i}" y="{bar_y}" width="2" height="{bar_h}" fill="{C["bg"]}"/>'
        for i in range(18, bar_w, 18)
    )

    perks = ["Problem Solver", "Quick Learner", "Team Player", "Detail-Oriented", "Time Manager"]
    chips, cx = [], 112
    for i, p in enumerate(perks):
        w = round(len(p) * 7.3 + 26)
        chips.append(
            f'<g class="chip" style="animation-delay:{1.2 + i * 0.15:.2f}s">'
            f'<rect x="{cx}" y="300" width="{w}" height="26" rx="4" fill="#1a1033" stroke="{C["mag"]}" stroke-opacity="0.7"/>'
            f'<text x="{cx + 10}" y="317.5" class="chipt" fill="{C["yellow"]}">★</text>'
            f'<text x="{cx + 22}" y="317.5" class="chipt" fill="{C["text"]}">{escape(p)}</text></g>'
        )
        cx += w + 8

    body = f"""
<defs>{COMMON_DEFS}
<linearGradient id="xp" x1="0" x2="1"><stop offset="0" stop-color="{C['cyan']}"/><stop offset="1" stop-color="{C['green']}"/></linearGradient>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{C['panel']}"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="13" fill="none" stroke="{C['cyan']}" stroke-opacity="0.55" stroke-width="2"/>
<rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="9" fill="none" stroke="{C['mag']}" stroke-opacity="0.25"/>
<text x="36" y="46" class="head" fill="{C['cyan']}">◆ PLAYER PROFILE</text>
<g class="blink"><circle cx="{W - 200}" cy="41" r="6" fill="{C['green']}"/></g>
<text x="{W - 36}" y="46" class="head" fill="{C['green']}" text-anchor="end">OPEN TO WORK</text>
<line x1="36" y1="58" x2="{W - 36}" y2="58" stroke="{C['cyan']}" stroke-opacity="0.2"/>
<rect x="36" y="70" width="190" height="190" rx="6" fill="{C['bg']}" stroke="{C['cyan']}" stroke-opacity="0.6"/>
<g class="bob">{avatar}<g class="lids">{lids}</g></g>
<text x="131" y="283" class="tag" fill="{C['text']}" text-anchor="middle">SAK522 <tspan fill="{C['yellow']}">· LV GRAD'26</tspan></text>
{''.join(info)}
<text x="262" y="246" class="small" fill="{C['dim']}">EXP BAR</text>
<text x="{bar_x + bar_w}" y="246" class="small" fill="{C['yellow']}" text-anchor="end">NEXT LEVEL ▸ FULL-TIME BACKEND ROLE</text>
<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" fill="#1f2937"/>
<rect x="{bar_x}" y="{bar_y}" width="{fill_w}" height="{bar_h}" fill="url(#xp)">
  <animate attributeName="width" from="0" to="{fill_w}" begin="0.3s" dur="1.8s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>
</rect>
{segs}
<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" fill="none" stroke="{C['cyan']}" stroke-opacity="0.7"/>
<text x="36" y="318" class="head2" fill="{C['mag']}">PERKS ▸</text>
{''.join(chips)}
<rect width="{W}" height="{H}" rx="14" fill="url(#scan)"/>
"""
    style = f"""
.head{{font:700 15px {FONT};letter-spacing:3px}}
.head2{{font:700 14px {FONT};letter-spacing:2px}}
.row{{font:700 15px {FONT}}}
.small{{font:700 12px {FONT};letter-spacing:1px}}
.tag{{font:700 13px {FONT};letter-spacing:1px}}
.chipt{{font:700 12px {FONT}}}
.blink{{animation:bl 1.2s steps(1) infinite}}
@keyframes bl{{0%{{opacity:1}}50%{{opacity:.15}}}}
.bob{{animation:bob 2.4s ease-in-out infinite}}
@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-3px)}}}}
.lids{{opacity:0;animation:lid 4.5s steps(1) infinite}}
@keyframes lid{{0%{{opacity:0}}94%{{opacity:1}}97%{{opacity:0}}}}

@keyframes pop{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
"""
    write("player-card.svg", svg(W, H, body, style, "Player profile: T. Sakthi, Backend Developer from Tamil Nadu, India"))


# ======================================================== 3. SKILL TREE
U, P, L = "U", "P", "L"
TREE = [
    ("LANGUAGES", [("Python", U), ("Java", U)]),
    ("BACKEND", [("REST APIs", U), ("Django", U), ("Flask", U), ("FastAPI", U), ("JWT Auth", U)]),
    ("DATA", [("SQL", U), ("PostgreSQL", U), ("SQLAlchemy", U), ("Data Analytics", U)]),
    ("AI / ML", [("Machine Learning", U), ("RAG Pipelines", P), ("Vector DBs", L), ("LLM APIs", L)]),
    ("TOOLS", [("Git", U), ("pytest", U), ("Docker", P), ("Cloud Deploy", P)]),
]


def lock_icon(x, y, col, s=1.0):
    """10x13 padlock drawn at (x, y), scaled by s."""
    return (
        f'<g transform="translate({x:g} {y:g}) scale({s:g})">'
        f'<path d="M2 5 v-2 a3 3 0 0 1 6 0 v2" fill="none" stroke="{col}" stroke-width="1.6"/>'
        f'<rect x="0" y="5" width="10" height="8" rx="1.5" fill="{col}"/></g>'
    )


def skill_tree():
    W, H = 840, 440
    col_cx = [100 + 160 * i for i in range(5)]
    nw, nh = 152, 34
    root_y, head_y, node_y0, step = 62, 134, 190, 48

    counts = {U: 0, P: 0, L: 0}
    lines, heads, nodes = [], [], []
    k = 0
    for ci, (branch, items) in enumerate(TREE):
        cx = col_cx[ci]
        lines.append(f'<path d="M{W / 2} {root_y + 36} V{root_y + 54} H{cx} V{head_y}" class="wire"/>')
        last_y = node_y0 + (len(items) - 1) * step + nh / 2
        lines.append(f'<path d="M{cx} {head_y + nh} V{last_y}" class="wire"/>')
        heads.append(
            f'<rect x="{cx - nw / 2}" y="{head_y}" width="{nw}" height="{nh}" rx="5" fill="#1a1033" stroke="{C["mag"]}"/>'
            f'<text x="{cx}" y="{head_y + 22}" class="bh" fill="{C["mag"]}" text-anchor="middle">{escape(branch)}</text>'
        )
        for ni, (label, state) in enumerate(items):
            counts[state] += 1
            x, y = cx - nw / 2, node_y0 + ni * step
            delay = f"animation-delay:{0.25 + k * 0.07:.2f}s"
            k += 1
            if state == U:
                nodes.append(
                    f'<g class="node" style="{delay}">'
                    f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="5" fill="#062a33" stroke="{C["cyan"]}"/>'
                    f'<rect x="{x + 9}" y="{y + 11}" width="12" height="12" rx="2" fill="{C["green"]}"/>'
                    f'<path d="M{x + 11.5} {y + 17} l3 3 l5 -6" fill="none" stroke="{C["bg"]}" stroke-width="2"/>'
                    f'<text x="{x + 29}" y="{y + 22}" class="nt" fill="{C["text"]}">{escape(label)}</text></g>'
                )
            elif state == P:
                nodes.append(
                    f'<g class="node" style="{delay}">'
                    f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="5" fill="#2a2306" stroke="{C["yellow"]}" class="dash"/>'
                    f'<circle cx="{x + 15}" cy="{y + 17}" r="6" fill="none" stroke="{C["yellow"]}" stroke-width="2"/>'
                    f'<path d="M{x + 15} {y + 11} a6 6 0 0 1 0 12 z" fill="{C["yellow"]}"/>'
                    f'<text x="{x + 29}" y="{y + 22}" class="nt" fill="{C["yellow"]}">{escape(label)}</text></g>'
                )
            else:
                nodes.append(
                    f'<g class="node" style="{delay}">'
                    f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="5" fill="#111827" stroke="{C["grey"]}"/>'
                    + lock_icon(x + 10, y + 10, C["grey_l"])
                    + f'<text x="{x + 29}" y="{y + 22}" class="nt" fill="{C["grey_l"]}">{escape(label)}</text></g>'
                )

    legend = (
        f'<rect x="452" y="28" width="11" height="11" rx="2" fill="{C["green"]}"/>'
        f'<text x="469" y="38" class="lg" fill="{C["text"]}">UNLOCKED {counts[U]}</text>'
        f'<rect x="586" y="28" width="11" height="11" rx="2" fill="{C["yellow"]}"/>'
        f'<text x="603" y="38" class="lg" fill="{C["text"]}">LEVELING {counts[P]}</text>'
        f'<rect x="716" y="28" width="11" height="11" rx="2" fill="{C["grey_l"]}"/>'
        f'<text x="733" y="38" class="lg" fill="{C["text"]}">LOCKED {counts[L]}</text>'
    )

    body = f"""
<defs>{COMMON_DEFS}</defs>
<rect width="{W}" height="{H}" rx="14" fill="{C['panel']}"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="13" fill="none" stroke="{C['cyan']}" stroke-opacity="0.55" stroke-width="2"/>
<text x="28" y="40" class="head" fill="{C['cyan']}">◆ SKILL TREE</text>
{legend}
{''.join(lines)}
<rect x="{W / 2 - 140}" y="{root_y}" width="280" height="36" rx="6" fill="#062a33" stroke="{C['cyan']}" stroke-width="2" filter="url(#glow)"/>
<text x="{W / 2}" y="{root_y + 23}" class="root" fill="{C['text']}" text-anchor="middle">CORE ▸ CS FUNDAMENTALS</text>
{''.join(heads)}
{''.join(nodes)}
<rect width="{W}" height="{H}" rx="14" fill="url(#scan)"/>
"""
    style = f"""
.head{{font:700 15px {FONT};letter-spacing:3px}}
.root{{font:700 14px {FONT};letter-spacing:2px}}
.bh{{font:700 13px {FONT};letter-spacing:2px}}
.nt{{font:700 12px {FONT}}}
.lg{{font:700 11.5px {FONT};letter-spacing:1px}}
.wire{{fill:none;stroke:{C['cyan']};stroke-opacity:.45;stroke-width:2;stroke-dasharray:4 4;animation:flow 1.2s linear infinite}}
@keyframes flow{{to{{stroke-dashoffset:-16}}}}
.dash{{stroke-dasharray:6 4;animation:flow 1s linear infinite}}

@keyframes pop{{from{{opacity:0}}to{{opacity:1}}}}
"""
    write("skill-tree.svg", svg(W, H, body, style, "Skill tree: Python, Java, Django, Flask, FastAPI, REST APIs, SQL, PostgreSQL, Machine Learning, Git and more"))


# ======================================================== 4. ACHIEVEMENTS
ACH = [
    (True, "INTERN CLEARED", "Coolman", "Innovations · 2025"),
    (True, "DEGREE UNLOCKED", "B.E. Computer", "Science · 2026"),
    (True, "API SHIPPED", "Expense Tracker", "REST API · FastAPI"),
    (True, "ALL TESTS GREEN", "20 / 20 pytest", "tests passing"),
    (True, "ML EXPLORER", "Smart Agriculture", "Decision Support"),
    (False, "LIVE IN PROD", "Deploy an API", "to the cloud"),
    (False, "AI ENGINEER", "Ship the RAG", "Q&A API"),
]


def achievements():
    W, H = 840, 296
    cw, ch, gap = 192, 96, 12
    done = sum(1 for a in ACH if a[0])
    cards = []
    positions = [(18 + i * (cw + gap), 66) for i in range(4)]
    positions += [(120 + i * (cw + gap), 174) for i in range(3)]
    for i, ((unlocked, t, s1, s2), (x, y)) in enumerate(zip(ACH, positions)):
        mx, my = x + 36, y + ch / 2
        delay = f"animation-delay:{0.2 + i * 0.12:.2f}s"
        if unlocked:
            cards.append(
                f'<g class="card" style="{delay}">'
                f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="8" fill="#1a1405" stroke="{C["yellow"]}" stroke-opacity="0.85"/>'
                f'<circle cx="{mx}" cy="{my}" r="27" fill="{C["yellow"]}" class="halo" filter="url(#softglow)"/>'
                f'<circle cx="{mx}" cy="{my}" r="23" fill="url(#medal)" stroke="{C["gold_d"]}" stroke-width="2"/>'
                f'<text x="{mx}" y="{my + 8}" class="star" text-anchor="middle" fill="#5a3d00">★</text>'
                f'<text x="{x + 66}" y="{y + 32}" class="at" fill="{C["yellow"]}">{escape(t)}</text>'
                f'<text x="{x + 66}" y="{y + 54}" class="as" fill="{C["text"]}">{escape(s1)}</text>'
                f'<text x="{x + 66}" y="{y + 71}" class="as" fill="{C["dim"]}">{escape(s2)}</text></g>'
            )
        else:
            cards.append(
                f'<g class="card" style="{delay}">'
                f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="8" fill="#111827" stroke="{C["grey"]}" stroke-dasharray="5 4"/>'
                f'<circle cx="{mx}" cy="{my}" r="23" fill="#1f2937" stroke="{C["grey"]}" stroke-width="2"/>'
                + lock_icon(mx - 8, my - 10.5, C["grey_l"], 1.6)
                + f'<text x="{x + 66}" y="{y + 32}" class="at" fill="{C["grey_l"]}">{escape(t)}</text>'
                f'<text x="{x + 66}" y="{y + 54}" class="as" fill="{C["dim"]}">{escape(s1)}</text>'
                f'<text x="{x + 66}" y="{y + 71}" class="as" fill="{C["grey_l"]}">{escape(s2)}</text></g>'
            )

    prog_w = 160
    body = f"""
<defs>{COMMON_DEFS}
<radialGradient id="medal" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#fff3b0"/><stop offset="0.55" stop-color="{C['yellow']}"/><stop offset="1" stop-color="#d49b00"/></radialGradient>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{C['panel']}"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="13" fill="none" stroke="{C['yellow']}" stroke-opacity="0.5" stroke-width="2"/>
<text x="28" y="42" class="head" fill="{C['yellow']}">◆ ACHIEVEMENTS</text>
<text x="{W - 28 - prog_w - 14}" y="42" class="head2" fill="{C['text']}" text-anchor="end">{done} / {len(ACH)}</text>
<rect x="{W - 28 - prog_w}" y="30" width="{prog_w}" height="14" fill="#1f2937" stroke="{C['yellow']}" stroke-opacity="0.6"/>
<rect x="{W - 28 - prog_w}" y="30" width="{prog_w * done / len(ACH):.1f}" height="14" fill="{C['yellow']}">
  <animate attributeName="width" from="0" to="{prog_w * done / len(ACH):.1f}" begin="0.4s" dur="1.4s" fill="freeze"/>
</rect>
{''.join(cards)}
<rect width="{W}" height="{H}" rx="14" fill="url(#scan)"/>
"""
    style = f"""
.head{{font:700 15px {FONT};letter-spacing:3px}}
.head2{{font:700 14px {FONT};letter-spacing:2px}}
.at{{font:700 11.5px {FONT}}}
.as{{font:700 10.5px {FONT}}}
.star{{font:700 24px {FONT}}}
.halo{{opacity:.25;animation:pulse 2.2s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:.15}}50%{{opacity:.55}}}}

@keyframes pop{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
"""
    write("achievements.svg", svg(W, H, body, style, "Achievements: 5 of 7 unlocked"))


# ======================================================== 5. FOOTER
def footer():
    W, H = 840, 140
    gs = "GAME SAVED"
    px = 5
    gx = (W - pixel_text_width(gs, px)) / 2
    body = f"""
<defs>{COMMON_DEFS}</defs>
<rect width="{W}" height="{H}" rx="14" fill="{C['bg']}"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="13" fill="none" stroke="{C['green']}" stroke-opacity="0.45" stroke-width="2"/>
<g filter="url(#glow)">{pixel_text(gs, gx, 30, px, C['green'])}</g>
<text x="{W / 2}" y="92" class="t" fill="{C['text']}" text-anchor="middle">Thanks for visiting, Player 2.  CONTINUE?  <tspan fill="{C['yellow']}" class="blink">▶ YES</tspan></text>
<text x="{W / 2}" y="118" class="s" fill="{C['dim']}" text-anchor="middle">T. SAKTHI · SAK522 · BUILT WITH PYTHON + SVG</text>
<rect width="{W}" height="{H}" rx="14" fill="url(#scan)"/>
"""
    style = f"""
.t{{font:700 15px {FONT};letter-spacing:1px}}
.s{{font:700 11px {FONT};letter-spacing:2px}}
.blink{{animation:bl 1s steps(1) infinite}}
@keyframes bl{{0%{{opacity:1}}50%{{opacity:0}}}}
"""
    write("game-saved.svg", svg(W, H, body, style, "Game saved. Thanks for visiting."))


if __name__ == "__main__":
    title_screen()
    player_card()
    skill_tree()
    achievements()
    footer()
