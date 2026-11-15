"""archkit: real-looking architecture / deployment-topology diagrams (AWS, on-premise, hybrid).

Builds on diagramkit.py + icons.py (a hand-placed SVG kit in the draw.io / AWS-architecture style) and adds:
  - extra AWS icons (ecs, ecr, cloudfront, sqs, vectordb, lambda, apigw, eks, rds, elasticache, efs reuse)
  - on-premise icons (firewall, router, switch, lb, vm, k8s, db, nas, vpn, internet, dns, proxy, directory,
    bastion, mq, cache, monitor, backup-onprem, hsm) in a muted palette so they never pass for AWS services
  - on-premise groups (dc, dmz, zone-app, zone-data, zone-mgmt, rack, cluster, site, partner)
  - badge-numbered connectors + a "what talks to what, how" table and a "deployed as" table
  - render(): HTML page (figure + tables) and PNG; lint(): finds lines running through text

Usage (from any folder):
    import sys; sys.path.insert(0, "<this skill>/scripts")   # e.g. ~/.claude/skills/diagram-atlas/scripts
    from archkit import *
"""
import os
import re
import subprocess
from xml.sax.saxutils import escape

import diagramkit
import icons
from diagramkit import (GREEN, INK, MUTED, PINK, T, az, badge, chain, group, icon, icon_l, icon_r,  # noqa: F401
                        lines, path, pipeline, sequence, svg)

BLUE = "#147EBA"
W = icons.W

# ------------------------------------------------------------------ icons
from glyphs import TAGS as _TAGS  # noqa: E402  (also registers the extra icons in icons.GLYPH)

diagramkit.GROUP.update({
    "dc": dict(stroke="#232F3E", dash="", fill="none", tag="t-dc", color="#232F3E"),
    "dmz": dict(stroke="none", dash="", fill="#FDF1E8", tag="t-dmz", color="#A2410F"),
    "zone-app": dict(stroke="none", dash="", fill="#E8F2FA", tag="t-zone", color="#1E5F8A"),
    "zone-data": dict(stroke="none", dash="", fill="#ECEEFB", tag="t-data", color="#2E3FA0"),
    "zone-mgmt": dict(stroke="none", dash="", fill="#F2EEF8", tag="t-mgmt", color="#5B3A8C"),
    "rack": dict(stroke="#455A64", dash="4 3", fill="none", tag="t-rack", color="#455A64"),
    "cluster": dict(stroke="#326CE5", dash="6 4", fill="none", tag="t-cluster", color="#326CE5"),
    "site": dict(stroke="#2E7D32", dash="6 4", fill="none", tag="t-site", color="#2E7D32"),
    "partner": dict(stroke="#6D4C41", dash="5 4", fill="#FBF8F6", tag="t-partner", color="#6D4C41"),
})


def symbols():
    """All icon, group-tag and marker definitions; embed once per HTML page."""
    base = icons.symbols()
    extra = "".join(f'<symbol id="{k}" viewBox="0 0 24 24"><rect width="24" height="24" fill="{c}"/>{g}</symbol>'
                    for k, (c, g) in _TAGS.items())
    extra += ('<marker id="arr-g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
              '<path d="M0 0L10 5L0 10z" fill="#1D7A46"/></marker>'
              '<marker id="arr-p" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
              '<path d="M0 0L10 5L0 10z" fill="#B0084D"/></marker>'
              '<marker id="arr-m" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
              '<path d="M0 0L10 5L0 10z" fill="#5A6B7B"/></marker>')
    return base.replace("</defs></svg>", extra + "</defs></svg>")


# ------------------------------------------------------------------ helpers
def label(x, y, text, anchor="start", size=12.5, fill=MUTED, weight="normal"):
    """Free text, e.g. a subnet or zone name placed where no line passes (see references/layout.md)."""
    return T(x, y, text, size, anchor, weight, fill)


def box(x, y, w, h, title=""):
    """Light card (team or service boundary). Title top-left; keep it short so vertical lines clear it."""
    return group(x, y, w, h, "box", title, 11.5)


def flow(pts, n=None, at=None, kind="data"):
    """Connector through orthogonal points with an optional numbered badge.
    kind: web or data (both solid ink: the name says what travels, the table says how) | static (dashed blue)
          | ops (dashed pink) | sync (dashed green) | out (dotted grey)
    at: badge position (x, y); default is the midpoint of the longest segment."""
    style = {"data": (INK, "", "arr"), "web": (INK, "", "arr"), "static": (BLUE, "5 4", "arr-b"),
             "ops": (PINK, "5 4", "arr-p"), "sync": (GREEN, "5 4", "arr-g"), "out": (MUTED, "3 3", "arr-m")}[kind]
    out = path(pts, style[0], style[1], style[2])
    if n is not None:
        if at is None:
            segs = list(zip(pts, pts[1:]))
            (x1, y1), (x2, y2) = max(segs, key=lambda s: abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1]))
            at = ((x1 + x2) / 2, (y1 + y2) / 2)
        out += badge(at[0], at[1], n)
    return out


def figure(width, height, parts):
    return svg(width, height, "".join(parts))


# ------------------------------------------------------------------ check
_TEXT = re.compile(r'<text x="([\d.]+)" y="([\d.]+)" font-size="([\d.]+)" text-anchor="(\w+)"[^>]*>([^<]*)</text>')
_PATH = re.compile(r'<path d="M([^"]+)" fill="none" stroke="([^"]+)"')


def lint(fig):
    """Report connector segments that run through a text label, badges on top of each other, and arrowheads
    hidden under an icon. Text width is estimated
    (Thai/Latin ≈ 0.56 × font size per character), so treat hits as places to look at, then look at the PNG."""
    texts = []
    for x, y, size, anchor, s in _TEXT.findall(fig):
        x, y, size = float(x), float(y), float(size)
        if s.strip().isdigit() and len(s.strip()) <= 2:
            continue                                  # badge numbers sit on lines on purpose
        w = len(s) * size * 0.56
        x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
        texts.append((x0, y - size * 0.8, x0 + w, y + size * 0.25, s))
    hits = []
    for d, _stroke in _PATH.findall(fig):
        pts = [tuple(map(float, p.split())) for p in d.replace("L", "|").split("|")]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            for x0, y0, x1, y1, s in texts:
                if ax == bx and x0 + 2 < ax < x1 - 2 and min(ay, by) < y1 and max(ay, by) > y0:
                    hits.append(f'vertical x={ax:g} crosses "{s}"')
                elif ay == by and y0 < ay < y1 and min(ax, bx) < x1 - 2 and max(ax, bx) > x0 + 2:
                    hits.append(f'horizontal y={ay:g} crosses "{s}"')
    hits += _badge_clashes(fig) + _buried_arrows(fig)
    return sorted(set(hits))


_BADGE = re.compile(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="10"')
_ICON = re.compile(r'<use href="#i-([\w-]+)" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"')
_ARROW = re.compile(r'<path d="M([^"]+)"[^>]*marker-end=')


def _badge_clashes(fig):
    """Two badges closer than 22 px read as one blob."""
    pts = [(float(x), float(y)) for x, y in _BADGE.findall(fig)]
    out = []
    for i, (ax, ay) in enumerate(pts):
        for bx, by in pts[i + 1:]:
            if (ax - bx) ** 2 + (ay - by) ** 2 < 22 ** 2:
                out.append(f"badges at ({ax:g},{ay:g}) and ({bx:g},{by:g}) overlap")
    return out


def _buried_arrows(fig):
    """An arrowhead that ends more than 4 px inside an icon is hidden under it."""
    boxes = [(n, float(x), float(y), float(w), float(h)) for n, x, y, w, h in _ICON.findall(fig)]
    out = []
    for d in _ARROW.findall(fig):
        ex, ey = map(float, d.replace("L", "|").split("|")[-1].split())
        for n, x, y, w, h in boxes:
            if x + 4 < ex < x + w - 4 and y + 4 < ey < y + h - 4:
                out.append(f"arrow ending at ({ex:g},{ey:g}) is hidden under icon {n}")
    return out


# ------------------------------------------------------------------ output
CSS = """:root{--navy:#1B2A4A;--blue:#1F6FB2;--ink:#232F3E;--muted:#5A6B7B;--line:#D5DCE4;--bg:#F4F6F9}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.6 "Noto Sans Thai",Tahoma,Arial,sans-serif}
main{max-width:1280px;margin:0 auto;padding:28px 16px 48px}
h1{color:var(--navy);font-size:24px;margin:0 0 4px}h2{color:var(--navy);font-size:18px;margin:28px 0 8px}
p.lead{color:var(--muted);margin:0 0 16px}
figure{margin:0;background:#fff;border:1px solid var(--line);padding:12px;overflow-x:auto}
figure svg{min-width:900px}figcaption{color:var(--muted);font-size:13px;margin-top:6px;text-align:center}
.wrap{overflow-x:auto}table{width:100%;min-width:760px;border-collapse:collapse;background:#fff;table-layout:fixed}
th{background:var(--blue);color:#fff;text-align:left;font-weight:600;padding:8px 10px}
td{border-bottom:1px solid var(--line);padding:8px 10px;vertical-align:top;overflow-wrap:anywhere}
td:first-child{font-weight:600}"""

HEADS = {
    "th": dict(talks=["#", "จาก → ถึง", "วิธีเชื่อมต่อ", "การยืนยันตัวตนและการจำกัดสิทธิ์"],
               deploy=["Component", "Deploy เป็น", "ทีมที่ดูแล"],
               t1="ตารางที่ 1 อะไรคุยกับอะไร และคุยอย่างไร", t2="ตารางที่ 2 แต่ละ component deploy เป็นอะไร",
               cap="รูปที่ 1 {title} หมายเลขบนเส้นตรงกับตารางที่ 1"),
    "en": dict(talks=["#", "From → to", "How they connect", "Authentication and access limits"],
               deploy=["Component", "Deployed as", "Owner"],
               t1="Table 1 What talks to what, and how", t2="Table 2 How each component is deployed",
               cap="Figure 1 {title}. Numbers on the lines match Table 1"),
}


def _table(head, rows, widths):
    cols = "".join(f'<col style="width:{w}">' for w in widths)
    th = "".join(f"<th>{escape(h)}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{escape(str(c))}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="wrap"><table><colgroup>{cols}</colgroup><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def page(title, lead, fig, talks=(), deploy=(), lang="th", caption=None):
    h = HEADS[lang]
    cap = caption or h["cap"].format(title=title)
    body = (f'<h1>{escape(title)}</h1><p class="lead">{escape(lead)}</p>'
            f'<figure>{symbols()}{fig}<figcaption>{escape(cap)}</figcaption></figure>')
    if talks:
        body += f'<h2>{h["t1"]}</h2>' + _table(h["talks"], talks, ["5%", "24%", "33%", "38%"])
    if deploy:
        body += f'<h2>{h["t2"]}</h2>' + _table(h["deploy"], deploy, ["30%", "50%", "20%"])
    return (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)}</title>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;600;700&display=swap">'
            f'<style>{CSS}</style></head><body><main>{body}</main></body></html>')


CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def png(fig, out_png, width=1400):
    """Screenshot just the figure with headless Chrome (the PNG is what you look at to check the layout)."""
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', fig)
    vw, vh = (float(m.group(1)), float(m.group(2))) if m else (1260, 800)
    height = int(width * vh / vw) + 4
    html = os.path.splitext(out_png)[0] + ".preview.html"
    open(html, "w", encoding="utf-8").write(
        f'<!doctype html><meta charset=utf-8><body style="margin:0;background:#fff">{symbols()}'
        f'<div style="width:{width}px">{fig}</div>')
    chrome = os.environ.get("CHROME", CHROME)
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={width},{height}",
                    f"--screenshot={out_png}", f"file://{os.path.abspath(html)}"], capture_output=True, timeout=60)
    os.remove(html)
    return out_png


def render(out_base, title, lead, fig, talks=(), deploy=(), lang="th", caption=None):
    """Write <out_base>.html (figure + tables) and <out_base>.png, print lint hits, return the paths."""
    html_path, png_path = out_base + ".html", out_base + ".png"
    for p in (html_path, png_path):
        if os.path.exists(p):
            print(f"overwriting {p}")
    open(html_path, "w", encoding="utf-8").write(page(title, lead, fig, talks, deploy, lang, caption))
    png(fig, png_path)
    hits = lint(fig)
    print(f"wrote {html_path}\nwrote {png_path}\nlint: {'clean' if not hits else str(len(hits)) + ' place(s) to look at'}")
    for h in hits:
        print("  -", h)
    return html_path, png_path
