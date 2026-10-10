#!/usr/bin/env python3
"""palette.py - brand palette from a logo (or a hex), built in OKLCH.

  build     logo image (png/jpg/webp/svg) or --brand hex  ->  tonal scales (50-950)
            for brand / accent / tinted neutral / success / warning / danger / info,
            light + dark semantic tokens chosen by contrast, and a contrast report.
            Writes tokens.css, tailwind-theme.css, tokens.json (DTCG),
            palette-report.md and preview.html into --out.
  contrast  FG BG [FG BG ...]  ->  WCAG 2.x ratio + APCA Lc for each pair.

Examples:
  python3 palette.py build --logo logo.png --out ./palette
  python3 palette.py build --brand "#0F62FE" --accent "#FF7A00" --out ./palette
  python3 palette.py contrast "#ffffff" "#0F62FE" "#6b7280" "#ffffff"

Needs Python 3.8+. Pillow is needed only for raster logos (pip install pillow).
SVG logos are read by parsing their fill/stroke colors (no rendering).
"""
import argparse
import json
import math
import os
import random
import re
import sys
from collections import Counter

VERSION = "2026.10.10-3"
STEPS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
# Lightness targets (OKLCH L) modelled on Tailwind v4's OKLCH palette.
CHROMA_L = [0.975, 0.940, 0.885, 0.810, 0.710, 0.630, 0.555, 0.490, 0.430, 0.380, 0.270]
NEUTRAL_L = [0.985, 0.967, 0.922, 0.870, 0.708, 0.556, 0.439, 0.371, 0.269, 0.205, 0.145]
# Chroma relative to the scale's peak, per step.
CHROMA_PROFILE = [0.06, 0.14, 0.27, 0.50, 0.80, 0.96, 1.00, 0.90, 0.76, 0.62, 0.42]
NEUTRAL_PROFILE = [0.25, 0.35, 0.50, 0.65, 1.00, 1.00, 0.95, 0.90, 0.75, 0.70, 0.65]
# Status hues in OKLCH degrees, nudged toward the brand hue when building.
STATUS = {  # "range" = hues that still read as that status (danger never drifts into orange)
    "success": {"h": 150.0, "c": 0.17, "l": 0.60, "range": (135, 165)},
    "warning": {"h": 75.0, "c": 0.17, "l": 0.77, "range": (60, 90)},
    "danger": {"h": 27.0, "c": 0.21, "l": 0.58, "range": (10, 32)},
    "info": {"h": 245.0, "c": 0.16, "l": 0.60, "range": (225, 265)},
}
CHROMATIC_MIN = 0.035  # below this OKLCH chroma a color reads as neutral


# --------------------------------------------------------------------------- color math
def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def cbrt(x):
    return math.copysign(abs(x) ** (1 / 3), x)


def rgb_to_oklab(rgb):
    r, g, b = (srgb_to_linear(v) for v in rgb)
    l_ = cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m_ = cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s_ = cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_linear(lab):
    L, a, b = lab
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def oklab_to_oklch(lab):
    L, a, b = lab
    C = math.hypot(a, b)
    H = math.degrees(math.atan2(b, a)) % 360
    return (L, C, H)


def oklch_to_oklab(lch):
    L, C, H = lch
    return (L, C * math.cos(math.radians(H)), C * math.sin(math.radians(H)))


def in_gamut(lch, eps=1e-4):
    return all(-eps <= v <= 1 + eps for v in oklab_to_linear(oklch_to_oklab(lch)))


def gamut_map(lch):
    """Keep L and H, reduce chroma until the color fits sRGB (CSS Color 4 style)."""
    L, C, H = lch
    L = min(max(L, 0.0), 1.0)
    if in_gamut((L, C, H)):
        return (L, C, H)
    lo, hi = 0.0, C
    for _ in range(30):
        mid = (lo + hi) / 2
        if in_gamut((L, mid, H)):
            lo = mid
        else:
            hi = mid
    return (L, lo, H)


def oklch_to_rgb(lch):
    lin = oklab_to_linear(oklch_to_oklab(gamut_map(lch)))
    return tuple(min(max(linear_to_srgb(min(max(v, 0.0), 1.0)), 0.0), 1.0) for v in lin)


def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) in (3, 4):
        h = "".join(ch * 2 for ch in h[:3])
    if len(h) not in (6, 8) or not re.fullmatch(r"[0-9a-fA-F]+", h):
        raise ValueError("not a hex color: %r" % h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#" + "".join("%02x" % int(round(min(max(v, 0), 1) * 255)) for v in rgb)


def hex_to_oklch(h):
    return oklab_to_oklch(rgb_to_oklab(hex_to_rgb(h)))


def oklch_css(lch):
    L, C, H = gamut_map(lch)
    if C < 0.0005:
        return "oklch(%.2f%% 0 0)" % (L * 100)
    return "oklch(%.2f%% %.4f %.2f)" % (L * 100, C, H)


def hue_dist(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def hue_toward(h, target, amount):
    """Rotate hue h toward target by at most `amount` degrees (shortest arc)."""
    d = (target - h + 540) % 360 - 180
    step = max(-amount, min(amount, d))
    return (h + step) % 360


def delta_e(l1, l2):
    return math.dist(l1, l2)


# --------------------------------------------------------------------------- contrast
def wcag_luminance(rgb):
    r, g, b = (srgb_to_linear(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def wcag_ratio(fg, bg):
    a, b = wcag_luminance(hex_to_rgb(fg)), wcag_luminance(hex_to_rgb(bg))
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def apca_lc(fg, bg):
    """APCA-W3 0.0.98G-4g lightness contrast (Lc). Positive = dark text on light bg."""
    def y(h):
        r, g, b = hex_to_rgb(h)
        v = 0.2126729 * r ** 2.4 + 0.7151522 * g ** 2.4 + 0.0721750 * b ** 2.4
        return v + (0.022 - v) ** 1.414 if v < 0.022 else v

    yt, yb = y(fg), y(bg)
    if abs(yb - yt) < 0.0005:
        return 0.0
    if yb > yt:
        sapc = (yb ** 0.56 - yt ** 0.57) * 1.14
        out = 0.0 if sapc < 0.1 else sapc - 0.027
    else:
        sapc = (yb ** 0.65 - yt ** 0.62) * 1.14
        out = 0.0 if sapc > -0.1 else sapc + 0.027
    return out * 100


def grade(ratio, need):
    return "PASS" if ratio >= need else "FAIL"


# --------------------------------------------------------------------------- logo reading
def read_svg_colors(path):
    text = open(path, encoding="utf-8", errors="ignore").read()
    found = Counter()
    for m in re.finditer(r"(?:fill|stroke|stop-color|color)\s*[:=]\s*[\"']?\s*(#[0-9a-fA-F]{3,8})\b", text):
        found[rgb_to_hex(hex_to_rgb(m.group(1)))] += 1
    for m in re.finditer(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", text):
        found[rgb_to_hex(tuple(int(v) / 255 for v in m.groups()))] += 1
    if not found:
        raise SystemExit("No hex/rgb fill colors found in %s. Pass --brand instead." % path)
    total = sum(found.values())
    return [{"hex": h, "share": n / total} for h, n in found.most_common()], None


def kmeans(points, k, iters=25, seed=7):
    rnd = random.Random(seed)
    centers = [rnd.choice(points)]
    while len(centers) < k:  # k-means++ init, deterministic seed
        d2 = [min(delta_e(p, c) ** 2 for c in centers) for p in points]
        total = sum(d2)
        if total == 0:
            break
        r, acc = rnd.random() * total, 0.0
        for p, d in zip(points, d2):
            acc += d
            if acc >= r:
                centers.append(p)
                break
    for _ in range(iters):
        groups = [[] for _ in centers]
        for p in points:
            groups[min(range(len(centers)), key=lambda i: delta_e(p, centers[i]))].append(p)
        new = [tuple(sum(v[j] for v in g) / len(g) for j in range(3)) if g else c
               for g, c in zip(groups, centers)]
        if all(delta_e(a, b) < 1e-5 for a, b in zip(new, centers)):
            break
        centers = new
    return centers, [len(g) for g in groups]


def seg_dist(p, a, b):
    """Distance from p to segment a-b in OKLab, and the projection parameter t."""
    ab = [b[i] - a[i] for i in range(3)]
    L2 = sum(v * v for v in ab) or 1e-12
    t = max(0.0, min(1.0, sum((p[i] - a[i]) * ab[i] for i in range(3)) / L2))
    return math.dist(p, [a[i] + t * ab[i] for i in range(3)]), t


def read_raster_colors(path, k):
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit("Pillow is required for raster logos: pip install pillow (or pass --brand HEX).")
    img = Image.open(path).convert("RGBA")
    nearest = getattr(getattr(Image, "Resampling", Image), "NEAREST")
    img.thumbnail((200, 200), nearest)          # nearest-neighbour: never invents in-between colours
    w, h = img.size
    px = img.load()
    border = [px[x, y] for x in range(w) for y in (0, 1, h - 2, h - 1)] + \
             [px[x, y] for y in range(h) for x in (0, 1, w - 2, w - 1)]
    background = None
    opaque_border = [p[:3] for p in border if p[3] >= 200]
    if len(opaque_border) > len(border) * 0.6:
        quant = Counter((r // 6, g // 6, b // 6) for r, g, b in opaque_border)
        q, n = quant.most_common(1)[0]
        if n > len(opaque_border) * 0.6:      # exact most common colour inside the dominant bucket
            exact = Counter(c for c in opaque_border if (c[0] // 6, c[1] // 6, c[2] // 6) == q).most_common(1)[0][0]
            background = rgb_to_hex(tuple(v / 255 for v in exact))
    bg_lab = rgb_to_oklab(hex_to_rgb(background)) if background else None
    pts = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            lab = rgb_to_oklab((r / 255, g / 255, b / 255))
            if bg_lab and delta_e(lab, bg_lab) < 0.06:
                continue
            pts.append((lab, (r, g, b)))
    if not pts:
        raise SystemExit("Logo has no foreground pixels after removing the background. Pass --brand.")
    sample = pts if len(pts) <= 5000 else random.Random(3).sample(pts, 5000)
    centers, _ = kmeans([p for p, _ in sample], min(k, len(sample)))
    merged = []  # merge near-duplicate centres
    for c in centers:
        if not any(delta_e(c, m) < 0.045 for m in merged):
            merged.append(c)
    groups = [Counter() for _ in merged]
    for lab, rgb in pts:                       # exact colours per cluster, over all pixels
        groups[min(range(len(merged)), key=lambda i: delta_e(lab, merged[i]))][rgb] += 1
    total = sum(sum(g.values()) for g in groups)
    clusters = []
    for c, g in zip(merged, groups):
        n = sum(g.values())
        if not n:
            continue
        mode, mn = g.most_common(1)[0]
        rep = tuple(v / 255 for v in mode) if mn >= 0.05 * n else oklch_to_rgb(oklab_to_oklch(c))
        clusters.append({"hex": rgb_to_hex(rep), "share": n / total, "lab": rgb_to_oklab(rep)})
    clusters.sort(key=lambda c: -c["share"])
    anchors = [c["lab"] for c in clusters] + ([bg_lab] if bg_lab else [])
    for c in clusters:                         # a small colour lying between two others = anti-aliasing blend
        if c["share"] >= 0.12:
            continue
        others = [a for a in anchors if a is not c["lab"]]
        for i in range(len(others)):
            for j in range(i + 1, len(others)):
                d, t = seg_dist(c["lab"], others[i], others[j])
                if d < 0.035 and 0.1 < t < 0.9:
                    c["blend"] = True
    out = [{"hex": c["hex"], "share": c["share"], "blend": c.get("blend", False)}
           for c in clusters if c["share"] >= 0.02]
    return out, background


def describe(colors):
    for c in colors:
        c["oklch"] = hex_to_oklch(c["hex"])
        c["chromatic"] = c["oklch"][1] >= CHROMATIC_MIN
    return colors


def is_ink(c):
    """Dark, low-chroma logo colors (black, navy, charcoal wordmarks) are text colors, not accents."""
    L, C, _ = c["oklch"]
    return L < 0.40 and C < 0.10


def pick_brand(colors):
    chroma = [c for c in colors if c["chromatic"] and not c.get("blend")]
    if chroma:  # a colourful mark beats a large black wordmark
        return max(chroma, key=lambda c: (c["share"] ** 0.6) * (c["oklch"][1] ** 0.4)), False
    return max(colors, key=lambda c: c["share"]), True


def assign_roles(colors, brand_hex):
    """Suggested role per extracted color: brand, ink (text), accent candidate, light tint, or noise."""
    ink = None
    for c in sorted(colors, key=lambda c: c["oklch"][0]):
        if c["hex"] != brand_hex and is_ink(c):
            ink = c["hex"]
            break
    for c in colors:
        L, C, _ = c["oklch"]
        if c.get("blend"):
            c["role"] = "anti-aliasing blend (ignored)"
        elif c["hex"] == brand_hex:
            c["role"] = "brand"
        elif c["hex"] == ink:
            c["role"] = "ink (text color)"
        elif is_ink(c):
            c["role"] = "dark neutral"
        elif C >= CHROMATIC_MIN:
            c["role"] = "accent candidate"
        elif L > 0.9:
            c["role"] = "light tint / background"
        else:
            c["role"] = "neutral (anti-aliasing or gray)"
    return ink


def push_away(h, hue_range, others, min_d=20.0):
    """Keep a status hue inside hue_range and at least min_d from every brand/accent hue,
    preferring the hue closest to h. Returns (hue, hues it still collides with)."""
    lo, hi = hue_range
    h = min(max(h, lo), hi)
    if all(hue_dist(h, o) >= min_d for o in others):
        return h, []
    cands = list(range(int(lo), int(hi) + 1))
    ok = [c for c in cands if all(hue_dist(c, o) >= min_d for o in others)]
    if ok:
        return float(min(ok, key=lambda c: hue_dist(c, h))), []
    best = float(max(cands, key=lambda c: min(hue_dist(c, o) for o in others)))
    return best, [o for o in others if hue_dist(best, o) < min_d]


# --------------------------------------------------------------------------- scales
def nearest_step(L, targets):
    return min(range(len(targets)), key=lambda i: abs(targets[i] - L))


def build_scale(seed_lch, exact_hex=None):
    """Tonal scale 50-950 anchored on the seed: the nearest step IS the seed color."""
    L0, C0, H0 = seed_lch
    a = nearest_step(L0, CHROMA_L)
    shift = L0 - CHROMA_L[a]
    weights = {0: 1.0, 1: 0.5, 2: 0.25}
    peak = min(C0 / CHROMA_PROFILE[a], max(C0 * 2.2, 0.05))
    yellow = 60 <= H0 <= 115
    scale = []
    for i, L in enumerate(CHROMA_L):
        L = L + shift * weights.get(abs(i - a), 0.0)
        H = H0
        if yellow and L < L0:  # dark yellows go olive; drift toward amber like Tailwind
            H = H0 - 28 * min(1.0, (L0 - L) / max(L0 - 0.25, 1e-6))
        lch = (L0, C0, H0) if i == a else (L, peak * CHROMA_PROFILE[i], H % 360)
        lch = gamut_map(lch)
        hx = exact_hex if (i == a and exact_hex) else rgb_to_hex(oklch_to_rgb(lch))
        scale.append({"step": STEPS[i], "oklch": lch, "hex": hx, "anchor": i == a})
    return scale


def build_neutral(hue, tint):
    return [{"step": STEPS[i], "oklch": gamut_map((L, tint * NEUTRAL_PROFILE[i], hue)),
             "hex": rgb_to_hex(oklch_to_rgb((L, tint * NEUTRAL_PROFILE[i], hue))), "anchor": False}
            for i, L in enumerate(NEUTRAL_L)]


def step(scale, s):
    return next(x for x in scale if x["step"] == s)


def anchor(scale):
    return next(x for x in scale if x["anchor"])


def harmony_seed(h, bL, bC):
    """A usable accent at hue h: oranges/yellows need high L or they read brown/olive."""
    L = 0.74 if 40 <= h <= 120 else min(max(bL, 0.55), 0.68)
    return rgb_to_hex(oklch_to_rgb((L, max(bC, 0.14), h)))


def harmonies(h):
    rot = lambda d: (h + d) % 360
    return {
        "complementary": [rot(180)],
        "analogous": [rot(-30), rot(30)],
        "split-complementary": [rot(150), rot(210)],
        "triadic": [rot(120), rot(240)],
        "tetradic": [rot(90), rot(180), rot(270)],
    }


# --------------------------------------------------------------------------- theme choice
def best_fg(bg_hex, light_fg, dark_fg):
    a, b = wcag_ratio(light_fg, bg_hex), wcag_ratio(dark_fg, bg_hex)
    return (light_fg, a) if a >= 4.5 or a >= b else (dark_fg, b)


def label_ok(fg, fill, apca_min):
    return wcag_ratio(fg, fill) >= 4.5 and abs(apca_lc(fg, fill)) >= apca_min


def choose_fill(scale, light_fg, dark_fg, prefer, bg_hex, min_bg=1.0):
    """First step in `prefer` order with a label color that passes WCAG 4.5:1 AND
    APCA |Lc| 60 (mid-tone oranges pass one but not the other), and that reaches
    `min_bg` against the page background. If none passes both, WCAG alone decides."""
    for apca_min in (60, 0):
        for s in prefer:
            c = step(scale, s)
            if wcag_ratio(c["hex"], bg_hex) < min_bg:
                continue
            for fg in (light_fg, dark_fg):
                if label_ok(fg, c["hex"], apca_min):
                    return c, fg
    c = step(scale, prefer[0])
    return c, best_fg(c["hex"], light_fg, dark_fg)[0]


def order_from(scale, start_step, direction):
    idx = STEPS.index(start_step)
    rest = STEPS[idx + 1:] if direction > 0 else list(reversed(STEPS[:idx]))
    other = list(reversed(STEPS[:idx])) if direction > 0 else STEPS[idx + 1:]
    return [start_step] + rest + other


def first_passing(scale, order, bg_hex, need):
    for s in order:
        if wcag_ratio(step(scale, s)["hex"], bg_hex) >= need:
            return step(scale, s)
    return step(scale, order[-1])


def first_readable(scale, order, bg_hex, apca_min=60):
    """First step that passes WCAG 4.5:1 and APCA |Lc| >= apca_min on bg (WCAG alone as fallback)."""
    for s in order:
        h = step(scale, s)["hex"]
        if wcag_ratio(h, bg_hex) >= 4.5 and abs(apca_lc(h, bg_hex)) >= apca_min:
            return step(scale, s)
    return first_passing(scale, order, bg_hex, 4.5)


def theme_tokens(sc, mode):
    """Semantic tokens named like templates/tokens-starter.css, so this output can replace
    the template's color section as-is."""
    n, b, ac = sc["neutral"], sc["brand"], sc["accent"]
    white, black = "#ffffff", step(n, 950)["hex"]
    a_step = anchor(b)["step"]
    ink = sc.get("_ink")
    if mode == "light":
        bg, surface = step(n, 50)["hex"], white
        raised, sunken = white, step(n, 100)["hex"]
        text = ink if ink and wcag_ratio(ink, bg) >= 7 else step(n, 950)["hex"]
        muted = first_readable(n, [600, 700, 800], bg)["hex"]
        disabled, inverse = step(n, 400)["hex"], step(n, 50)["hex"]
        border = step(n, 200)["hex"]
        border_strong = first_passing(n, [400, 500, 600, 700], surface, 3.0)["hex"]
        prim, prim_fg = choose_fill(b, white, text, order_from(b, a_step, +1), bg)
        i = STEPS.index(prim["step"])
        prim_hover, prim_active = step(b, STEPS[min(i + 1, 10)])["hex"], step(b, STEPS[min(i + 2, 10)])["hex"]
        acc, acc_fg = choose_fill(ac, white, text, order_from(ac, anchor(ac)["step"], +1), bg)
        link = first_passing(b, order_from(b, max(a_step, 600), +1), bg, 4.5)["hex"]
        ring = first_passing(b, order_from(b, 500, +1), bg, 3.0)["hex"]
        p_subtle, p_subtle_fg = step(b, 100)["hex"], step(b, 800)["hex"]
        a_subtle = step(ac, 100)["hex"]
        fill_order, text_order, subtle_step = [600, 700, 800], [700, 600, 800], 50
    else:
        bg, surface = step(n, 950)["hex"], step(n, 900)["hex"]
        raised, sunken = step(n, 800)["hex"], rgb_to_hex(oklch_to_rgb((0.12, step(n, 950)["oklch"][1], step(n, 950)["oklch"][2])))
        text = step(n, 50)["hex"]
        muted = first_readable(n, [400, 300, 200], bg)["hex"]  # WCAG 2 overstates contrast on dark
        disabled, inverse = step(n, 600)["hex"], step(n, 950)["hex"]
        border = step(n, 800)["hex"]
        border_strong = first_passing(n, [600, 500, 400, 300], surface, 3.0)["hex"]
        # Keep the exact brand color when it works on dark; otherwise go lighter, never darker first.
        lighter_first = lambda a: [a] + sorted((s for s in STEPS if s != a),
                                               key=lambda s: (s > 600, abs(s - min(a, 400))))
        order = STEPS if sc["_mono"] else lighter_first(a_step)  # mono brands invert: near-white fill
        prim, prim_fg = choose_fill(b, white, black, order, bg, min_bg=3.0)
        i = STEPS.index(prim["step"])
        prim_hover, prim_active = step(b, STEPS[max(i - 1, 0)])["hex"], step(b, STEPS[max(i - 2, 0)])["hex"]
        order = STEPS if sc["_mono"] and ac[0]["oklch"][1] < CHROMATIC_MIN else lighter_first(anchor(ac)["step"])
        acc, acc_fg = choose_fill(ac, white, black, order, bg, min_bg=3.0)
        link = first_readable(b, [400, 300, 200, 100], bg)["hex"]   # WCAG 2 overstates contrast on dark
        ring = first_passing(b, [400, 300, 200], bg, 3.0)["hex"]
        p_subtle, p_subtle_fg = step(b, 900)["hex"], step(b, 200)["hex"]
        a_subtle = step(ac, 900)["hex"]
        fill_order, text_order, subtle_step = [500, 400, 600], [300, 400, 200], 950
    t = {
        "bg": bg, "surface": surface, "surface-raised": raised, "surface-sunken": sunken,
        "text": text, "text-muted": muted, "text-disabled": disabled, "text-inverse": inverse,
        "link": link, "border": border, "border-strong": border_strong,
        "primary": prim["hex"], "primary-hover": prim_hover, "primary-active": prim_active,
        "primary-foreground": prim_fg, "primary-subtle": p_subtle, "primary-subtle-foreground": p_subtle_fg,
        "accent": acc["hex"], "accent-foreground": acc_fg, "accent-subtle": a_subtle,
        "focus-ring": ring,
    }
    for k in STATUS:
        fill, fill_fg = choose_fill(sc[k], white, black, fill_order, bg)
        if delta_e(rgb_to_oklab(hex_to_rgb(fill["hex"])), rgb_to_oklab(hex_to_rgb(prim["hex"]))) < 0.1:
            # e.g. an orange brand's primary vs the amber warning: switch the status to a light fill + dark label
            light_order = [300, 200, 400] if mode == "light" else [200, 300, 100]
            fill, fill_fg = choose_fill(sc[k], white, black, light_order, bg)
        t[k] = fill["hex"]
        t[k + "-foreground"] = fill_fg
        t[k + "-subtle"] = step(sc[k], subtle_step)["hex"]
        t[k + "-text"] = first_passing(sc[k], text_order, bg, 4.5)["hex"]
    t["_primary_step"] = prim["step"]
    t["_accent_step"] = acc["step"]
    t["_mode"] = mode
    return t


def contrast_rows(t):
    pairs = [
        ("text on bg", t["text"], t["bg"], 4.5),
        ("text-muted on bg", t["text-muted"], t["bg"], 4.5),
        ("text-muted on surface-sunken", t["text-muted"], t["surface-sunken"], 4.5),
        ("primary-foreground on primary", t["primary-foreground"], t["primary"], 4.5),
        ("primary-subtle-foreground on primary-subtle", t["primary-subtle-foreground"], t["primary-subtle"], 4.5),
        ("accent-foreground on accent", t["accent-foreground"], t["accent"], 4.5),
        ("link on bg", t["link"], t["bg"], 4.5),
        ("danger-text on bg", t["danger-text"], t["bg"], 4.5),
        ("danger-foreground on danger", t["danger-foreground"], t["danger"], 4.5),
        ("primary fill vs bg (advisory)", t["primary"], t["bg"], 3.0),
        ("border-strong vs surface (non-text)", t["border-strong"], t["surface"], 3.0),
        ("focus-ring vs bg (non-text)", t["focus-ring"], t["bg"], 3.0),
    ]
    rows = []
    for name, fg, bg, need in pairs:
        r = wcag_ratio(fg, bg)
        result = grade(r, need)
        if "advisory" in name and result == "FAIL":
            result = "LOW"  # WCAG 1.4.11 doesn't require it when the label identifies the button
        rows.append({"pair": name, "fg": fg, "bg": bg, "ratio": r, "need": need,
                     "apca": apca_lc(fg, bg), "result": result})
    return rows


# --------------------------------------------------------------------------- writers
SCALE_NAMES = ["brand", "accent", "neutral", "success", "warning", "danger", "info"]


TEMPLATE_STATUS = {"success": "green", "warning": "amber", "danger": "red", "info": "blue"}


def css_scales(sc, prefix):
    """Ramps, plus the extra primitives templates/tokens-starter.css uses (--neutral-0/1000 and the
    red/green/amber/blue status ramps as aliases), so this file can replace the template's colour section."""
    b, a, n = anchor(sc["brand"])["oklch"], anchor(sc["accent"])["oklch"], step(sc["neutral"], 500)["oklch"]
    out = ["  /* hue/chroma seeds read by the template (elevation, generated ramps) */",
           "  --%sbrand-h: %.2f; --%sbrand-c: %.4f;" % (prefix, b[2], prefix, b[1]),
           "  --%saccent-h: %.2f; --%saccent-c: %.4f;" % (prefix, a[2], prefix, a[1]),
           "  --%sneutral-h: %.2f; --%sneutral-c: %.4f;" % (prefix, n[2], prefix, n[1]),
           "  --%sneutral-0: #ffffff;" % prefix]
    for name in SCALE_NAMES:
        for x in sc[name]:
            note = "  /* %s%s */" % (x["hex"], " brand anchor" if x["anchor"] and name == "brand" else "")
            out.append("  --%s%s-%d: %s;%s" % (prefix, name, x["step"], oklch_css(x["oklch"]), note))
    n950 = step(sc["neutral"], 950)["oklch"]
    out.append("  --%sneutral-1000: %s;" % (prefix, oklch_css((max(n950[0] - 0.07, 0.0), n950[1], n950[2]))))
    for status, alias in TEMPLATE_STATUS.items():
        for s_ in STEPS:
            out.append("  --%s%s-%d: var(--%s%s-%d);" % (prefix, alias, s_, prefix, status, s_))
    return "\n".join(out)


def css_theme(t, indent="  "):
    lines = ["%s--%s: %s;" % (indent, k, v) for k, v in t.items() if not k.startswith("_")]
    if t.get("_mode") == "dark":   # shadows read weaker on dark; the template's elevation tokens need these
        lines += ["%s--shadow-color: 0 0 0;" % indent, "%s--shadow-strength: 3;" % indent]
    else:
        lines += ["%s--shadow-color: 0.25 0.02 var(--neutral-h);" % indent, "%s--shadow-strength: 1;" % indent]
    return "\n".join(lines)


def write_css(sc, themes, prefix, path):
    css = """/* Generated by design-atlas/scripts/palette.py. OKLCH values are sRGB-gamut mapped. */
:root {
%s
}

/* Semantic tokens - light (default). Each theme scope re-declares color and
   background so a [data-theme] section inside the page doesn't inherit the
   parent's already-computed text color. */
:root, [data-theme="light"] {
  color-scheme: light;
%s
  color: var(--text);
  background-color: var(--bg);
}

/* Dark: follows the OS unless the page pins a theme with data-theme */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
%s
    color: var(--text);
    background-color: var(--bg);
  }
}
[data-theme="dark"] {
  color-scheme: dark;
%s
  color: var(--text);
  background-color: var(--bg);
}
""" % (css_scales(sc, prefix), css_theme(themes["light"]), css_theme(themes["dark"], "    "),
       css_theme(themes["dark"]))
    open(path, "w").write(css)


def write_tailwind(sc, prefix, path):
    lines = ["/* Tailwind v4: @import \"tailwindcss\"; then this file. Semantic tokens live in tokens.css. */",
             "@theme {"]
    for name in SCALE_NAMES:
        for x in sc[name]:
            lines.append("  --color-%s%s-%d: %s;" % (prefix, name, x["step"], oklch_css(x["oklch"])))
    for k in ["bg", "surface", "surface-raised", "surface-sunken", "text", "text-muted", "border",
              "border-strong", "primary", "primary-foreground", "primary-subtle", "accent",
              "accent-foreground", "link", "focus-ring", "success", "warning", "danger", "info"]:
        lines.append("  --color-%s: var(--%s);" % (k, k))
    lines.append("}")
    open(path, "w").write("\n".join(lines) + "\n")


def dtcg_color(lch, hx):
    L, C, H = gamut_map(lch)
    return {"$type": "color", "$value": {"colorSpace": "oklch",
                                         "components": [round(L, 4), round(C, 4), round(H, 2)],
                                         "hex": hx}}


def write_dtcg(sc, themes, path):
    doc = {"color": {name: {str(x["step"]): dtcg_color(x["oklch"], x["hex"]) for x in sc[name]}
                     for name in SCALE_NAMES}}
    for mode, t in themes.items():
        doc.setdefault("theme", {})[mode] = {
            k: {"$type": "color", "$value": {"colorSpace": "srgb",
                                             "components": [round(v, 4) for v in hex_to_rgb(val)],
                                             "hex": val}}
            for k, val in t.items() if not k.startswith("_")}
    json.dump(doc, open(path, "w"), indent=2)


def md_table(rows, cols):
    head = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n"
    return head + "\n".join("| " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows) + "\n"


def write_report(info, sc, themes, path):
    o = ["# Palette report", ""]
    if info["source"]:
        o.append("Source: `%s`%s" % (info["source"], "  (logo canvas %s left out of the extraction)" % info["background"]
                                     if info["background"] else ""))
        if info["background"] and hex_to_oklch(info["background"])[1] >= 0.008:
            o.append("")
            o.append("The logo sits on a tinted canvas (%s). If that colour is part of the brand, use it as the page "
                     "background (`--bg`) and re-check `text`/`text-muted` contrast against it." % info["background"])
        o.append("")
        o.append(md_table([{"hex": c["hex"], "share": "%.0f%%" % (c["share"] * 100),
                            "oklch": oklch_css(c["oklch"]), "suggested role": c.get("role", "")}
                           for c in info["extracted"]], ["hex", "share", "oklch", "suggested role"]))
    b = anchor(sc["brand"])
    o.append("**Brand:** %s %s, anchored at step %d. **Accent:** %s (%s).%s" % (
        b["hex"], oklch_css(b["oklch"]), b["step"], anchor(sc["accent"])["hex"], info["accent_reason"],
        " **Ink (light-theme text):** %s." % sc["_ink"] if sc.get("_ink") else ""))
    o.append("")
    if info["warnings"]:
        o.append("## Warnings")
        o.extend("- " + w for w in info["warnings"])
        o.append("")
    o.append("## Harmony candidates (hue only; build a scale with --accent to try one)")
    for name, hues in ({} if sc["_mono"] else harmonies(b["oklch"][2])).items():
        sw = ", ".join(harmony_seed(h, b["oklch"][0], b["oklch"][1]) for h in hues)
        o.append("- %s: %s" % (name, sw))
    o.append("")
    o.append("## Scales")
    rows = []
    for i, s in enumerate(STEPS):
        rows.append(dict({"step": s}, **{n: sc[n][i]["hex"] + ("*" if sc[n][i]["anchor"] and n in ("brand", "accent") else "")
                                          for n in SCALE_NAMES}))
    o.append(md_table(rows, ["step"] + SCALE_NAMES))
    o.append("`*` = anchor step (the exact input color).")
    o.append("")
    for mode in ("light", "dark"):
        t = themes[mode]
        o.append("## %s theme" % mode.title())
        o.append("Primary fill uses brand-%d." % t["_primary_step"])
        o.append("")
        o.append(md_table([{"token": k, "value": v} for k, v in t.items() if not k.startswith("_")], ["token", "value"]))
        rows = [dict(r, ratio="%.2f:1" % r["ratio"], need="%.1f:1" % r["need"],
                     apca="Lc %.0f%s" % (r["apca"], " (low)" if abs(r["apca"]) < (60 if r["need"] >= 4.5 else 30) else ""))
                for r in info["contrast"][mode]]
        o.append(md_table(rows, ["pair", "fg", "bg", "ratio", "need", "apca", "result"]))
    o.append("APCA guide (WCAG 3 draft, advisory): body text |Lc| >= 75 (60 minimum for larger text), "
             "large headlines >= 45, non-text UI >= 30. WCAG 2.x ratios above are the compliance gate; "
             "an APCA '(low)' on dark themes means WCAG 2 is overstating the contrast - consider a lighter step "
             "for long-form text.")
    open(path, "w").write("\n".join(o) + "\n")


PREVIEW = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Palette preview</title>
<style>
%(css)s
.light { %(light)s }
.dark { %(dark)s color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; font: 15px/1.55 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; background: #e9e9ec; color: #111; }
main { max-width: 1180px; margin: 0 auto; padding: 24px 16px 64px; }
h1 { font-size: 22px; margin: 0 0 4px; } .sub { color: #555; margin: 0 0 20px; }
.scale { display: grid; grid-template-columns: 90px repeat(11, 1fr); gap: 4px; margin-bottom: 6px; align-items: stretch; }
.scale b { font-size: 12px; align-self: center; }
.sw { height: 44px; border-radius: 6px; font-size: 10px; display: flex; align-items: flex-end; padding: 3px 5px; }
.sw.anchor { outline: 3px solid #111; outline-offset: 1px; }
.themes { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; margin-top: 24px; }
.panel { background: var(--bg); color: var(--text); border-radius: 16px; padding: 20px; border: 1px solid var(--border); }
.nav { display: flex; justify-content: space-between; align-items: center; padding-bottom: 14px; border-bottom: 1px solid var(--border); }
.logo { font-weight: 700; } .nav a { color: var(--link); text-decoration: none; margin-left: 14px; font-size: 14px; }
.hero h2 { font-size: 26px; line-height: 1.15; margin: 18px 0 8px; letter-spacing: -0.01em; }
.hero p { color: var(--text-muted); margin: 0 0 16px; }
.btn { border: 0; border-radius: 10px; padding: 10px 16px; font: inherit; font-weight: 600; cursor: pointer; margin-right: 8px; }
.btn.primary { background: var(--primary); color: var(--primary-foreground); } .btn.primary:hover { background: var(--primary-hover); }
.btn.accent { background: var(--accent); color: var(--accent-foreground); }
.btn.ghost { background: transparent; color: var(--text); box-shadow: inset 0 0 0 1px var(--border-strong); }
.btn:focus-visible { outline: 2px solid var(--focus-ring); outline-offset: 2px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 14px; margin-top: 16px; }
.card .muted { color: var(--text-muted); font-size: 13px; }
.chip { display: inline-block; background: var(--primary-subtle); color: var(--primary-subtle-foreground); border-radius: 999px; padding: 2px 10px; font-size: 12px; font-weight: 600; }
input { width: 100%%; margin-top: 6px; padding: 9px 11px; border-radius: 8px; border: 1px solid var(--border-strong); background: var(--surface); color: var(--text); font: inherit; }
.alerts { display: grid; gap: 8px; margin-top: 16px; }
.alert { border-radius: 10px; padding: 8px 12px; font-size: 13px; border-left: 4px solid; }
.alert.success { background: var(--success-subtle); border-color: var(--success); color: var(--success-text); }
.alert.warning { background: var(--warning-subtle); border-color: var(--warning); color: var(--text); }
.alert.danger { background: var(--danger-subtle); border-color: var(--danger); color: var(--danger-text); }
.alert.info { background: var(--info-subtle); border-color: var(--info); color: var(--info-text); }
table { border-collapse: collapse; width: 100%%; font-size: 12px; margin-top: 16px; }
td, th { text-align: left; padding: 4px 6px; border-bottom: 1px solid var(--border); }
.fail { color: var(--danger-text); font-weight: 700; }
@media (max-width: 640px) { .scale { grid-template-columns: 60px repeat(11, 1fr); } .sw { font-size: 0; } }
</style></head>
<body><main>
<h1>Palette preview</h1>
<p class="sub">Brand %(brand)s anchored at step %(astep)s &middot; accent %(accent)s &middot; outlined swatch = exact input color</p>
%(scales)s
<div class="themes">%(panels)s</div>
</main></body></html>
"""

PANEL = """<section class="panel %(mode)s">
  <div class="nav"><span class="logo">Brand</span><span><a href="#">Product</a><a href="#">Pricing</a><a href="#">Docs</a></span></div>
  <div class="hero"><span class="chip">%(mode)s theme</span>
    <h2>Design that matches your logo</h2>
    <p>Secondary text uses text-muted. Links and chips use the brand scale.</p>
    <button class="btn primary">Get started</button><button class="btn accent">Accent</button><button class="btn ghost">Secondary</button>
  </div>
  <div class="card"><b>Card on surface</b><div class="muted">Muted supporting text on a raised surface.</div>
    <label style="display:block;margin-top:10px;font-size:13px">Email<input placeholder="you@example.com"></label></div>
  <div class="alerts"><div class="alert success">Saved successfully.</div><div class="alert warning">Your trial ends in 3 days.</div>
    <div class="alert danger">Payment failed. Check your card.</div><div class="alert info">New version available.</div></div>
  <table><tr><th>pair</th><th>WCAG</th><th>APCA</th><th></th></tr>%(rows)s</table>
</section>"""


def write_preview(sc, themes, info, path):
    scales = []
    for name in SCALE_NAMES:
        cells = "".join('<div class="sw%s" style="background:%s;color:%s">%d</div>' % (
            " anchor" if x["anchor"] and name in ("brand", "accent") else "", x["hex"],
            best_fg(x["hex"], "#ffffff", "#000000")[0], x["step"]) for x in sc[name])
        scales.append('<div class="scale"><b>%s</b>%s</div>' % (name, cells))
    panels = []
    for mode in ("light", "dark"):
        rows = "".join("<tr><td>%s</td><td>%.2f:1</td><td>Lc %.0f</td><td class=\"%s\">%s</td></tr>" % (
            r["pair"], r["ratio"], r["apca"], "fail" if r["result"] == "FAIL" else "", r["result"])
            for r in info["contrast"][mode])
        panels.append(PANEL % {"mode": mode, "rows": rows})
    decl = lambda t: " ".join("--%s: %s;" % (k, v) for k, v in t.items() if not k.startswith("_"))
    html = PREVIEW % {"css": "", "light": decl(themes["light"]), "dark": decl(themes["dark"]),
                      "brand": anchor(sc["brand"])["hex"], "astep": anchor(sc["brand"])["step"],
                      "accent": anchor(sc["accent"])["hex"], "scales": "\n".join(scales),
                      "panels": "\n".join(panels)}
    open(path, "w").write(html)


# --------------------------------------------------------------------------- commands
def cmd_build(args):
    info = {"source": args.logo, "background": None, "extracted": [], "warnings": []}
    if args.logo:
        ext = os.path.splitext(args.logo)[1].lower()
        colors, info["background"] = (read_svg_colors(args.logo) if ext == ".svg"
                                      else read_raster_colors(args.logo, args.k))
        info["extracted"] = describe(colors)
    if args.brand:
        brand_hex, mono = rgb_to_hex(hex_to_rgb(args.brand)), False
        if hex_to_oklch(brand_hex)[1] < CHROMATIC_MIN:
            mono = True
    elif info["extracted"]:
        b, mono = pick_brand(info["extracted"])
        brand_hex = b["hex"]
    else:
        raise SystemExit("Give --logo PATH or --brand HEX.")
    bL, bC, bH = hex_to_oklch(brand_hex)
    ink = assign_roles(info["extracted"], brand_hex) if info["extracted"] else None
    if args.ink:
        ink = rgb_to_hex(hex_to_rgb(args.ink))

    if mono:
        info["warnings"].append(
            "Brand color %s is neutral (monochrome logo). The primary stays neutral; pass --accent HEX "
            "to give the UI one brand hue for links, focus and highlights." % brand_hex)

    # accent: explicit > second logo hue > harmony rule
    accent_hex, reason = None, ""
    if args.no_accent:
        accent_hex, reason = brand_hex, "single-colour brand (--no-accent): accent = brand"
    elif args.accent:
        accent_hex, reason = rgb_to_hex(hex_to_rgb(args.accent)), "given"
    elif args.harmony == "auto" and info["extracted"]:
        others = [c for c in info["extracted"] if c.get("role") == "accent candidate"
                  and hue_dist(c["oklch"][2], bH) >= 30 and c["share"] >= 0.02]
        if others:  # small vivid marks (a dot, a spark) are the accent; pick by chroma, not area
            accent_hex = max(others, key=lambda c: c["oklch"][1])["hex"]
            reason = "second hue in the logo"
    if not accent_hex:
        rule = "split-complementary" if args.harmony == "auto" else args.harmony
        if mono:
            accent_hex, reason = brand_hex, "monochrome brand (no accent hue given)"
        else:
            h = harmonies(bH).get(rule, harmonies(bH)["split-complementary"])[0]
            accent_hex = harmony_seed(h, bL, bC)
            reason = rule + " of the brand hue"

    sc = {"brand": build_scale(hex_to_oklch(brand_hex), brand_hex),
          "accent": build_scale(hex_to_oklch(accent_hex), accent_hex),
          "neutral": build_neutral(bH, 0.0 if mono else args.neutral_tint), "_mono": mono, "_ink": ink}
    aL, aC, aH = hex_to_oklch(accent_hex)
    vivid = [(name, hue) for name, hue, c in (("brand", bH, bC), ("accent", aH, aC))
             if c >= 0.08 and not (name == "accent" and hue_dist(aH, bH) < 1)]
    for k, s in STATUS.items():
        h = hue_toward(s["h"], bH, 0 if mono else args.status_pull)
        h, clash = push_away(h, s["range"], [hue for _, hue in vivid] if k != "info" else [])
        if k != "info":
            for name, hue in vivid:
                if hue in clash:
                    info["warnings"].append(
                        "%s hue %.0f is within 20 deg of the %s hue (%.0f; it can't move further and still read as %s): "
                        "never signal %s by color alone - pair it with an icon and label, and keep %s "
                        "visually distinct from %s elements." % (name.title(), hue, k, h, k, k, k, name))
        sc[k] = build_scale((s["l"], s["c"], h))
        if k in ("success", "danger") and not clash:
            near = [(nm, hu) for nm, hu in vivid if hue_dist(hu, h) < 30]
            for nm, hu in near:
                info["warnings"].append(
                    "%s hue %.0f is within 30 deg of %s (%.0f): readable, but pair %s messages with an icon and "
                    "keep %s-coloured buttons visually distinct from status banners." % (nm.title(), hu, k, h, k, nm))

    if bC > 0.25:
        info["warnings"].append("Brand chroma %.3f is very high: use it for small accents and CTAs, not large "
                                "surfaces; in dark mode the chosen primary step is lighter on purpose." % bC)
    if bL > 0.85 and not mono:
        info["warnings"].append("Brand color is very light (L %.2f): it can't carry white text or be body text; "
                                "use it as a fill with dark labels and use a darker step for links." % bL)

    themes = {m: theme_tokens(sc, m) for m in ("light", "dark")}
    info["contrast"] = {m: contrast_rows(themes[m]) for m in themes}
    info["accent_reason"] = reason
    a_step = anchor(sc["brand"])["step"]
    if themes["light"]["_primary_step"] != a_step:
        info["warnings"].append(
            "The exact brand color (step %d) has no label color that passes both WCAG 4.5:1 and APCA Lc 60, "
            "so the light-theme primary fill uses brand-%d. Keep the exact color for the logo and large graphics; "
            "run `contrast` to see the WCAG-only option." % (
                a_step, themes["light"]["_primary_step"]))
    acc_anchor = anchor(sc["accent"])
    if not mono and not args.no_accent and themes["light"]["_accent_step"] != acc_anchor["step"]:
        fill = step(sc["accent"], themes["light"]["_accent_step"])
        info["warnings"].append(
            "The exact accent %s can't carry a label that passes WCAG 4.5:1 and APCA Lc 60, so accent-filled buttons use "
            "accent-%d %s, which can read %s. Prefer the accent for decoration (dots, illustrations, highlights) "
            "and keep buttons on primary; or label the exact accent with near-black text if `contrast` shows it passes." % (
                acc_anchor["hex"], fill["step"], fill["hex"],
                "close to danger" if hue_dist(fill["oklch"][2], STATUS["danger"]["h"]) < 25 else "darker than the logo"))
    fails = [(m, r["pair"]) for m in info["contrast"] for r in info["contrast"][m] if r["result"] == "FAIL"]
    for m, p in fails:
        info["warnings"].append("%s theme: '%s' fails WCAG - adjust before shipping." % (m, p))
    for m in info["contrast"]:
        for r in info["contrast"][m]:
            if r["result"] == "LOW":
                info["warnings"].append(
                    "%s theme: primary fill is only %.2f:1 against the page. Fine for labelled buttons; "
                    "for chips/toggles/unlabelled controls add a border or use a darker brand step." % (m, r["ratio"]))

    os.makedirs(args.out, exist_ok=True)
    prefix = (args.prefix + "-") if args.prefix else ""
    write_css(sc, themes, prefix, os.path.join(args.out, "tokens.css"))
    write_tailwind(sc, prefix, os.path.join(args.out, "tailwind-theme.css"))
    write_dtcg(sc, themes, os.path.join(args.out, "tokens.json"))
    write_report(info, sc, themes, os.path.join(args.out, "palette-report.md"))
    write_preview(sc, themes, info, os.path.join(args.out, "preview.html"))

    summary = {
        "brand": brand_hex, "brand_oklch": oklch_css((bL, bC, bH)), "brand_anchor_step": a_step,
        "accent": accent_hex, "accent_reason": reason, "ink": ink, "monochrome": mono,
        "extracted": [{"hex": c["hex"], "share": round(c["share"], 3), "role": c.get("role")}
                      for c in info["extracted"]],
        "background_ignored": info["background"],
        "light_primary": themes["light"]["primary"], "dark_primary": themes["dark"]["primary"],
        "contrast_failures": ["%s: %s" % f for f in fails],
        "warnings": info["warnings"],
        "files": sorted(os.listdir(args.out)),
        "out": os.path.abspath(args.out),
    }
    print(json.dumps(summary, indent=2))


def parse_color(v):
    """#hex, or oklch(L C H) with L as 0-1 or a percentage, as written in CSS."""
    m = re.fullmatch(r"\s*oklch\(\s*([\d.]+)(%?)\s+([\d.]+)\s+([\d.]+)(?:deg)?\s*(?:/[^)]*)?\)\s*", v, re.I)
    if m:
        L = float(m.group(1)) / (100 if m.group(2) else 1)
        return rgb_to_hex(oklch_to_rgb((L, float(m.group(3)), float(m.group(4)))))
    return rgb_to_hex(hex_to_rgb(v))


def cmd_contrast(args):
    if len(args.colors) % 2:
        raise SystemExit("Give colors in FG BG pairs.")
    failed = 0
    for fg_in, bg_in in zip(args.colors[::2], args.colors[1::2]):
        fg, bg = parse_color(fg_in), parse_color(bg_in)
        r, lc = wcag_ratio(fg, bg), apca_lc(fg, bg)
        verdict = ("AAA body" if r >= 7 else "AA body" if r >= 4.5 else "AA large/UI only" if r >= 3 else "fails AA")
        line = "%s on %s: %.2f:1 (%s) | APCA Lc %.1f" % (fg_in, bg_in, r, verdict, lc)
        if args.need:
            ok = r >= args.need
            failed += not ok
            line += " | need %.1f:1 %s" % (args.need, "PASS" if ok else "FAIL")
        print(line)
    sys.exit(1 if failed else 0)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")
    b = sub.add_parser("build", help="build palette + tokens from a logo or a brand hex")
    b.add_argument("--logo", help="logo file: png, jpg, webp, gif or svg")
    b.add_argument("--brand", help="brand color hex; overrides the color picked from the logo")
    b.add_argument("--accent", help="accent color hex; default = 2nd logo hue or a harmony rule")
    b.add_argument("--no-accent", action="store_true", help="single-colour brand: no second hue (accent tokens = brand)")
    b.add_argument("--ink", help="text color hex for the light theme; default = the logo's dark wordmark color if any")
    b.add_argument("--harmony", default="auto",
                   choices=["auto", "complementary", "analogous", "split-complementary", "triadic", "tetradic"],
                   help="rule for the accent hue when the logo has no second hue (default auto)")
    b.add_argument("--neutral-tint", type=float, default=0.015,
                   help="OKLCH chroma of the brand-tinted neutrals (0 = pure gray, 0.03 = strong tint)")
    b.add_argument("--status-pull", type=float, default=10.0,
                   help="max degrees success/warning/danger/info hues lean toward the brand hue")
    b.add_argument("--k", type=int, default=6, help="colors to extract from raster logos")
    b.add_argument("--prefix", default="", help="prefix for ramp (primitive) names only, e.g. acme -> --acme-brand-500; "
                   "semantic tokens (--primary, --bg...) keep the template's names")
    b.add_argument("--out", default="palette-out", help="output directory")
    b.set_defaults(func=cmd_build)
    c = sub.add_parser("contrast", help="WCAG ratio + APCA Lc for FG BG pairs")
    c.add_argument("colors", nargs="+", help='#hex or "oklch(62% 0.19 260)", in FG BG pairs')
    c.add_argument("--need", type=float, help="required ratio (4.5 text, 3 large text/UI); exit 1 if any pair fails")
    c.set_defaults(func=cmd_contrast)
    if "--version" in sys.argv[1:]:
        print("palette.py " + VERSION); sys.exit(0)
    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
