"""
Build an animated "live engagement" terminal SVG for the ibfavas profile README.

A fake pentest against his own profile: whoami -> nmap (open ports = skills)
-> searchsploit (0 results) -> ./hire.sh -> ACCESS GRANTED.

Lines reveal sequentially via SMIL; the final cursor blinks. Honors the
STATIC env var (like make_info_card.py) to render a single static frame.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "favas-engagement.svg")
STATIC = bool(os.environ.get("STATIC"))

W = 860
TITLEBAR_H = 30
PAD_X = 22
TOP_PAD = 20
BOT_PAD = 20
LINE_H = 23
FS = 13

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#8b949e"
INK = "#e6edf3"
GREEN = "#3fb950"
BLUE = "#58a6ff"
PROMPT = "#3fb950"

# Each line: list of (color, text) segments, plus kind for animation timing.
LINES = [
    [("prompt", "favas@kali:~/engagements$ "), ("cmd", "whoami")],
    [("out", "favas")],
    [("prompt", "favas@kali:~/engagements$ "), ("cmd", "nmap -sV ibfavas --top-ports 4")],
    [("tbl", "PORT       SERVICE   CAPABILITY")],
    [("out", "80/tcp     http      Web Exploitation")],
    [("out", "443/tcp    https     Auth Bypass")],
    [("out", "514/tcp    syslog    Threat Detection")],
    [("out", "22/tcp     ssh       Linux Hardening")],
    [("prompt", "favas@kali:~/engagements$ "), ("cmd", "searchsploit favas")],
    [("out", "Exploits: 0 — target patches faster than you scan")],
    [("prompt", "favas@kali:~/engagements$ "), ("cmd", "./hire.sh")],
    [("ok", "[+] ACCESS GRANTED"), ("out", " — full report declassified below")],
]

COLORS = {
    "prompt": PROMPT,
    "cmd": INK,
    "out": MUTED,
    "tbl": BLUE,
    "ok": GREEN,
}

H = TITLEBAR_H + TOP_PAD + len(LINES) * LINE_H + BOT_PAD


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def reveal(inner, begin):
    if STATIC:
        return f"<g>{inner}</g>"
    return (
        f'<g opacity="0">{inner}'
        f'<animate attributeName="opacity" from="0" to="1" '
        f'begin="{begin:.2f}s" dur="0.35s" fill="freeze"/></g>'
    )


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    "<defs>"
    f'<linearGradient id="ebg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#ebg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD_X + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(
    f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
    f'text-anchor="middle">favas@kali: ~/engagements/ibfavas</text>'
)

delay = 0.4
for li, segs in enumerate(LINES):
    y = TITLEBAR_H + TOP_PAD + li * LINE_H + 4
    tspans = "".join(
        f'<tspan fill="{COLORS[kind]}">{esc(text)}</tspan>' for kind, text in segs
    )
    # measure last line width roughly for cursor placement (7.8px per char at 13px mono)
    line_text = "".join(t for _, t in segs)
    inner = f'<text x="{PAD_X}" y="{y:.1f}" font-size="{FS}">{tspans}</text>'
    if li == len(LINES) - 1 and not STATIC:
        cx = PAD_X + len(line_text) * 7.85 + 6
        inner += (
            f'<rect x="{cx:.1f}" y="{y - 11:.1f}" width="8" height="14" fill="{GREEN}">'
            f'<animate attributeName="opacity" values="1;0;1;1" keyTimes="0;0.45;0.55;1" '
            f'dur="1.1s" begin="{delay + 0.35:.2f}s" repeatCount="indefinite"/></rect>'
        )
    parts.append(reveal(inner, delay))
    delay += 0.55 if li % 4 == 3 else 0.4

parts.append("</svg>")

with open(OUT, "w") as f:
    f.write("\n".join(parts) + "\n")
print(f"Wrote {OUT} ({os.path.getsize(OUT)} bytes)")
