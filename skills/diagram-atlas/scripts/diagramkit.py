"""Hand-placed SVG diagram kit in the draw.io / AWS-architecture style.

Low-level helpers (T, lines, icon, icon_l, icon_r, group, az, path, badge, svg) let you place every
box yourself, the way a person does in draw.io. Three ready builders cover the common shapes:
sequence(), chain() and pipeline(). Architecture diagrams are always system-specific: lay them out
with group()/az()/icon_*() (see assets/example_content.py) and check them with preview().

Icons come from icons.py (`#i-<name>` symbols); the document must embed icons.symbols() once.
"""
import os
import subprocess
from xml.sax.saxutils import escape

FONT = 'font-family="Tahoma, Arial, sans-serif"'
INK = "#232F3E"
MUTED = "#5A6B7B"
GREEN = "#1D7A46"
PINK = "#B0084D"


# ------------------------------------------------------------------ primitives
def T(x, y, s, size=13, anchor="start", weight="normal", fill=INK):
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" '
            f'fill="{fill}">{escape(str(s))}</text>')


def lines(x, y, rows, size=13, anchor="start", gap=None, first_bold=False, fill=INK):
    gap = gap or size + 3
    return "".join(T(x, y + i * gap, r, size, anchor, "bold" if (first_bold and i == 0) else "normal", fill)
                   for i, r in enumerate(rows))


def icon(cx, cy, name, size=44):
    h = size / 2
    return f'<use href="#i-{name}" x="{cx - h}" y="{cy - h}" width="{size}" height="{size}"/>'


def icon_l(cx, cy, name, label_rows, size=44, label_size=13, first_bold=True, gap=None):
    """Icon with its label centred underneath (AWS diagram convention)."""
    return icon(cx, cy, name, size) + lines(cx, cy + size / 2 + label_size + 3, label_rows, label_size,
                                             "middle", gap, first_bold)


def icon_r(cx, cy, name, label_rows, size=44, label_size=13, first_bold=True):
    """Icon with its label to the right — use when a line must enter the icon from below."""
    n = len(label_rows)
    y0 = cy - (n - 1) * (label_size + 3) / 2 + label_size / 3
    return icon(cx, cy, name, size) + lines(cx + size / 2 + 8, y0, label_rows, label_size, "start", None, first_bold)


GROUP = {
    "cloud": dict(stroke=INK, dash="", fill="none", tag="t-cloud", color=INK),
    "region": dict(stroke="#00A4A6", dash="6 4", fill="none", tag="t-region", color="#00A4A6"),
    "vpc": dict(stroke="#8C4FFF", dash="", fill="none", tag="t-vpc", color="#8C4FFF"),
    "pub": dict(stroke="none", dash="", fill="#F2F6E8", tag="t-pub", color="#4C7A0B"),
    "priv": dict(stroke="none", dash="", fill="#E6F6F7", tag="t-priv", color="#007A7C"),
    "plain": dict(stroke="#7D8998", dash="5 4", fill="none", tag=None, color=MUTED),
    "box": dict(stroke="#7D8998", dash="", fill="#FAFAFA", tag=None, color=INK),
}


def group(x, y, w, h, kind, label, size=12.5):
    """AWS group container: cloud / region / vpc / pub (public subnet) / priv (private subnet) / plain / box."""
    g = GROUP[kind]
    dash = f'stroke-dasharray="{g["dash"]}"' if g["dash"] else ""
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{g["fill"]}" stroke="{g["stroke"]}" stroke-width="1.3" {dash}/>'
    if g["tag"]:
        out += f'<use href="#{g["tag"]}" x="{x}" y="{y}" width="24" height="24"/>'
        out += T(x + 30, y + 16, label, size, "start", "normal", g["color"])
    elif label:
        out += T(x + 8, y + 16, label, size, "start", "normal", g["color"])
    return out


def az(x, y, w, h, label):
    """Availability-zone column: dashed blue, label centred on top."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#147EBA" stroke-width="1.3" stroke-dasharray="6 4"/>'
            + T(x + w / 2, y + 17, label, 12.5, "middle", "normal", "#147EBA"))


def path(pts, color=INK, dash="", marker="arr", width=1.5):
    """Orthogonal connector through the given points; marker=None for a plain line."""
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    m = f'marker-end="url(#{marker})"' if marker else ""
    da = f'stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" {da} {m}/>'


def badge(cx, cy, n, color=INK):
    return (f'<circle cx="{cx}" cy="{cy}" r="10" fill="{color}"/>' + T(cx, cy + 4.5, str(n), 12, "middle", "bold", "#fff"))


def svg(w, h, body):
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" {FONT}>'
            f'<rect width="{w}" height="{h}" fill="#fff"/>{body}</svg>')


# ------------------------------------------------------------------ builders
def sequence(actors, messages, note=None, width=920, gap=50):
    """Sequence diagram.

    actors:   [(icon_name, label), ...]  laid out left → right across `width`
    messages: [(from_idx, to_idx, text, kind), ...]  kind: "req" | "async" (dashed) | "ok" (green reply)
    note:     optional list of short lines, drawn as a yellow note bottom-right
    Text starts just after the step number on the left end of the arrow, so keep each message
    shorter than the distance between its two actors (≈ 6.5 px per character at 12.5 px).
    """
    n = len(actors)
    step = (width - 120) / max(n - 1, 1)
    xs = [60 + i * step for i in range(n)]
    top, y = 92, 130
    height = top + 40 + gap * len(messages) + (90 if note else 30)
    b = []
    for x, (ic, lab) in zip(xs, actors):
        b.append(icon(x, 40, ic, 40))
        b.append(T(x, 82, lab, 13, "middle", "bold"))
        b.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{height - 20}" stroke="#9AA5B1" stroke-dasharray="4 4"/>')
    colors = {"req": INK, "async": PINK, "ok": GREEN}
    for i, (a, c, text, kind) in enumerate(messages, 1):
        color = colors.get(kind, INK)
        xa, xc = xs[a], xs[c]
        b.append(path([(xa, y), (xc + (-6 if xc > xa else 6), y)], color, "5 4" if kind == "async" else ""))
        lo = min(xa, xc)
        b.append(badge(lo + 16, y - 13, i, color))
        b.append(T(lo + 32, y - 8, text, 12.5, "start", fill=color))
        y += gap
    if note:
        nh = 20 + 18 * len(note)
        b.append(f'<rect x="{width - 370}" y="{height - nh - 10}" width="355" height="{nh}" fill="#FFF8E5" stroke="#C9A227"/>')
        b.append(lines(width - 360, height - nh + 10, note, 11.5, "start", 18))
    return svg(width, height, "".join(b))


def chain(nodes, link_label="TLS", footer=None, width=870):
    """Layered chain (defence in depth, request path).

    nodes: [(icon_name or "cloudflare", label, [up to 3 short control bullets]), ...]
    """
    n = len(nodes)
    step = (width - 140) / max(n - 1, 1)
    b = []
    for i, (ic, lab, ctl) in enumerate(nodes):
        x = 70 + i * step
        if ic == "cloudflare":
            b.append(f'<use href="#i-cloudflare" x="{x - 32}" y="30" width="64" height="40"/>')
        else:
            b.append(icon(x, 50, ic, 44))
        b.append(T(x, 98, lab, 13, "middle", "bold"))
        b.append(f'<rect x="{x - 66}" y="112" width="132" height="{20 + 19 * max(len(ctl), 1)}" fill="#F7F9FB" stroke="#B8C2CC"/>')
        b.append(lines(x - 58, 132, ["• " + c for c in ctl], 11.5, "start", 19))
        if i < n - 1:
            b.append(path([(x + 32, 50), (x + step - 34, 50)]))
            if link_label:
                b.append(T(x + step / 2, 42, link_label, 10.5, "middle", fill=GREEN))
    h = 200
    if footer:
        b.append(f'<rect x="4" y="206" width="{width - 8}" height="28" fill="#EEF3F8" stroke="#B8C2CC"/>')
        b.append(T(width / 2, 225, footer, 12.5, "middle"))
        h = 240
    return svg(width, h, "".join(b))


def pipeline(steps, tail=None, side_box=None, width=870):
    """Numbered left → right process (release, onboarding, incident flow).

    steps:    [(icon_name, [label line 1, line 2]), ...]  max ~6 per row
    tail:     optional [(icon_name, [lines]), ...] drawn on a second row under the last step,
              flowing right (e.g. "SSM run → servers")
    side_box: optional (title, [box texts]) drawn bottom-left as a small boxed sub-flow
    """
    b = []
    step = (width - 120) / max(len(steps) - 1, 1)
    xs = [60 + i * step for i in range(len(steps))]
    for i, (ic, lab) in enumerate(steps):
        b.append(icon_l(xs[i], 60, ic, lab, 44, 12))
        b.append(badge(xs[i] - 30, 30, i + 1))
        if i < len(steps) - 1:
            b.append(path([(xs[i] + 28, 60), (xs[i + 1] - 30, 60)]))
    h = 150
    if tail:
        x0 = xs[-1] - 140 * (len(tail) - 1)
        b.append(path([(xs[-1], 128), (xs[-1], 165), (x0, 165), (x0, 185)]))
        for k, (ic, lab) in enumerate(tail):
            x = x0 + 140 * k
            b.append(icon_l(x, 210, ic, lab, 44, 12))
            b.append(badge(x - 30, 180, len(steps) + k + 1))
            if k < len(tail) - 1:
                b.append(path([(x + 25, 210), (x + 140 - 38, 210)]))
        h = 290
    if side_box:
        title, boxes = side_box
        bw = 96
        total = len(boxes) * (bw + 19) + 20
        b.append(group(10, 165, total, 110, "box", title, 12.5))
        for k, t in enumerate(boxes):
            x = 70 + k * (bw + 19)
            b.append(f'<rect x="{x - bw / 2}" y="205" width="{bw}" height="40" fill="#fff" stroke="#8C4FFF"/>')
            b.append(T(x, 230, t, 12, "middle"))
            if k < len(boxes) - 1:
                b.append(path([(x + bw / 2, 225), (x + bw / 2 + 17, 225)]))
        h = max(h, 290)
    return svg(width, h, "".join(b))


# ------------------------------------------------------------------ layout check
def preview(figures, out_png, chrome=None, width=1130):
    """Render diagrams to one PNG (each in a bordered frame) so you can look for overlaps
    before building the document. figures: list of SVG strings."""
    import icons
    chrome = chrome or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    html_path = os.path.splitext(out_png)[0] + ".html"
    body = "".join(f'<div style="width:{width - 30}px;margin:10px;border:1px solid #ddd">{f}</div>' for f in figures)
    open(html_path, "w", encoding="utf8").write(
        f'<!doctype html><meta charset=utf-8><body style="margin:0;background:#fff">{icons.symbols()}{body}')
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={width},{900 * len(figures)}", f"--screenshot={out_png}",
                    f"file://{html_path}"], capture_output=True)
    return out_png
