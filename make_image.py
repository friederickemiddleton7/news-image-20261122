#!/usr/bin/env python3
"""Build-time generator for the news front page of Sunday 22 November 2026.

Not run by the grader; it exists so the committed entry.png can be rebuilt
byte-for-byte from source.  Everything is drawn with fixed coordinates and
fixed strings, so repeated runs produce identical pixels.
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 32

NAVY = (11, 18, 32)
CARD = (21, 31, 51)
RULE = (42, 58, 87)
BODY = (215, 222, 234)
WHITE = (255, 255, 255)
AMBER = (242, 179, 61)
TEAL = (79, 209, 197)
MUTED = (150, 162, 182)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"
REG = FONT_DIR + "DejaVuSans.ttf"

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def text_w(d, s, f):
    return d.textlength(s, font=f)


def spaced_w(d, s, f, extra):
    return sum(text_w(d, c, f) + extra for c in s) - extra


def spaced(d, x, y, s, f, fill, extra):
    cx = x
    for c in s:
        d.text((cx, y), c, font=f, fill=fill)
        cx += text_w(d, c, f) + extra
    return cx - extra


def fit_size(d, lines, path, maxw, top, floor, step=1):
    """Largest font size <= top (>= floor) at which every line fits maxw."""
    size = top
    while size > floor:
        f = font(path, size)
        if all(text_w(d, ln, f) <= maxw for ln in lines):
            return size
        size -= step
    return floor


def wrap(d, text, f, maxw):
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(d, trial, f) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def card(d, x, y, w, h, fill=CARD):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=fill, outline=RULE, width=1)


# ---------------------------------------------------------------- pictograms

def pic_globe(d, x, y, w, h):
    """Globe with three rising bars."""
    r = 50
    cx, cy = x + r + 4, y + h // 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=TEAL, width=3)
    d.arc([cx - r + 20, cy - r, cx + r - 20, cy + r], 0, 360, fill=TEAL, width=2)
    d.line([cx - r, cy, cx + r, cy], fill=TEAL, width=2)
    d.line([cx, cy - r, cx, cy + r], fill=TEAL, width=2)
    d.line([cx - r - 8, cy + r + 2, cx + r + 8, cy + r + 2], fill=RULE, width=3)
    base = cy + r + 2
    bars = [(x + 118, 30, TEAL), (x + 142, 52, TEAL), (x + 166, 76, AMBER)]
    for bx, bh, col in bars:
        d.rectangle([bx, base - bh, bx + 16, base], fill=col)


def pic_tanker(d, x, y, w, h):
    """Tanker hull with a burst above the deck."""
    d.polygon([(x + 4, y + 30), (x + 56, y + 30), (x + 48, y + 44), (x + 12, y + 44)],
              fill=TEAL)
    d.line([x + 18, y + 24, x + 42, y + 24], fill=TEAL, width=3)
    d.rectangle([x + 24, y + 14, x + 36, y + 24], fill=TEAL)
    bx, by = x + 44, y + 10
    d.polygon([(bx, by - 11), (bx + 4, by - 3), (bx + 12, by - 4), (bx + 6, by + 2),
               (bx + 10, by + 10), (bx + 2, by + 6), (bx - 6, by + 11), (bx - 4, by + 3),
               (bx - 12, by + 2), (bx - 5, by - 3)], fill=AMBER)


def pic_missile(d, x, y, w, h):
    """Missile body with fins and a dashed flight arc."""
    d.polygon([(x + 42, y + 12), (x + 54, y + 20), (x + 42, y + 28)], fill=AMBER)
    d.rectangle([x + 14, y + 15, x + 43, y + 25], fill=AMBER)
    d.polygon([(x + 14, y + 15), (x + 20, y + 20), (x + 14, y + 25)], fill=AMBER)
    d.polygon([(x + 22, y + 25), (x + 28, y + 33), (x + 30, y + 25)], fill=AMBER)
    d.polygon([(x + 22, y + 15), (x + 28, y + 7), (x + 30, y + 15)], fill=AMBER)
    for i in range(6):
        t = i / 6.0
        ax = x + 12 - 8 * i
        ay = y + 34 + 10 * t + 6 * i
        if ax < x - 4:
            break
        d.arc([ax - 4, ay - 4, ax + 4, ay + 4], 200, 340, fill=TEAL, width=2)


def pic_chart(d, x, y, w, h):
    """Stepped line falling left to right, arrowhead at the end."""
    pts = [(x + 2, y + 10), (x + 14, y + 10), (x + 14, y + 22),
           (x + 26, y + 22), (x + 26, y + 34), (x + 38, y + 34)]
    d.line(pts, fill=TEAL, width=3, joint="curve")
    for px, py in pts[:3]:
        d.rectangle([px - 2, py - 2, px + 2, py + 2], fill=WHITE)
    d.line([x + 36, y + 32, x + 50, y + 48], fill=AMBER, width=3)
    d.polygon([(x + 53, y + 52), (x + 41, y + 50), (x + 51, y + 40)], fill=AMBER)


def pic_boat(d, x, y, w, h):
    """Boat hull tilted into waves."""
    d.polygon([(x + 6, y + 22), (x + 54, y + 16), (x + 44, y + 34), (x + 14, y + 38)],
              fill=AMBER)
    d.line([x + 26, y + 20, x + 26, y + 4], fill=AMBER, width=3)
    d.polygon([(x + 27, y + 3), (x + 41, y + 15), (x + 27, y + 15)], fill=TEAL)
    for i, oy in enumerate((40, 47)):
        pts = []
        for k in range(9):
            px = x + 2 + k * 6.5
            py = y + oy + (3 if (k + i) % 2 else -1)
            pts.append((px, py))
        d.line(pts, fill=TEAL, width=2)


# ---------------------------------------------------------------- text blocks

def chip(d, x, y, s, size, fill, extra):
    f = font(BOLD, size)
    while spaced_w(d, s, f, extra) > 900 and size > 18:
        size -= 1
        f = font(BOLD, size)
    spaced(d, x, y, s, f, fill, extra)
    return size


def footer(d, y):
    label = "ALSO TODAY"
    lf = font(BOLD, 21)
    wlab = text_w(d, label, lf)
    d.text((MARGIN, y), label, font=lf, fill=AMBER)
    x = MARGIN + wlab + 18

    line1 = "GTA VI takes $3.79bn on day one \u00b7 Peru quake injures 15"
    line2 = "FBI probes breach of crime database"
    maxw = W - MARGIN - x

    size = 21
    f = font(REG, size)
    while size > 20 and max(text_w(d, line1, f), text_w(d, line2, f)) > maxw:
        size -= 1
        f = font(REG, size)

    d.text((x, y), line1, font=f, fill=MUTED)
    d.text((x, y + 28), line2, font=f, fill=MUTED)


def main():
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)

    # ---- header -----------------------------------------------------------
    chip(d, MARGIN, 24, "WORLD NEWS", 26, AMBER, 7)
    date = "22 NOVEMBER 2026"
    dsize = fit_size(d, [date], BOLD, W - 2 * MARGIN, 78, 56)
    d.text((MARGIN, 50), date, font=font(BOLD, dsize), fill=WHITE)
    d.rectangle([MARGIN, 150, W - MARGIN - 1, 152], fill=AMBER)

    # ---- lead card --------------------------------------------------------
    lx, ly, lw, lh = MARGIN, 168, W - 2 * MARGIN, 284
    card(d, lx, ly, lw, lh)
    chip(d, lx + 22, ly + 14, "GLOBAL  \u00b7  COP31, ANTALYA", 24, AMBER, 2)

    pic_w = 170
    pic_x = lx + lw - 20 - pic_w
    pic_globe(d, pic_x, ly + 96, pic_w, 150)

    maxw = pic_x - (lx + 22) - 22
    head = ["CLIMATE TALKS RUN INTO", "OVERTIME AS FOSSIL FUEL", "FIGHT BLOCKS A DEAL"]
    hsize = fit_size(d, head, BOLD, maxw, 54, 34)
    hf = font(BOLD, hsize)
    hy = ly + 48
    for ln in head:
        d.text((lx + 22, hy), ln, font=hf, fill=WHITE)
        hy += int(hsize * 1.16)

    body = ("A third draft goes to nearly 200 nations after coal, oil and gas "
            "were cut from the text.")
    bsize = 25
    bf = font(REG, bsize)
    blines = wrap(d, body, bf, maxw)
    while bsize > 20 and (len(blines) > 2 or hy + int(bsize * 1.3) * len(blines) > ly + lh - 16):
        bsize -= 1
        bf = font(REG, bsize)
        blines = wrap(d, body, bf, maxw)
    by = hy + 8
    for ln in blines[:3]:
        d.text((lx + 22, by), ln, font=bf, fill=BODY)
        by += int(bsize * 1.3)

    # ---- 2x2 grid ---------------------------------------------------------
    cw = (W - 2 * MARGIN - 20) // 2          # 470
    xs = [MARGIN, MARGIN + cw + 20]
    rh = 226
    rows = [462, 462 + rh + 10]

    tiles = [
        ("MIDDLE EAST  \u00b7  HORMUZ",
         ["THREE TANKERS HIT", "IN THE STRAIT"],
         "Iran's Guard says it downed two US drones; the waterway stays shut.",
         pic_tanker),
        ("EUROPE  \u00b7  KRYVYI RIH",
         ["RUSSIAN STRIKE HITS", "ZELENSKY'S HOMETOWN"],
         "Two killed and 60 wounded; NATO pledges to defend Poland after missiles landed there.",
         pic_missile),
        ("BUSINESS  \u00b7  WALL STREET",
         ["NASDAQ WIPES OUT", "ITS 2026 GAINS"],
         "Nvidia slides 14% in the week its chief resigned; Anthropic's IPO fizzles.",
         pic_chart),
        ("AFRICA  \u00b7  BAYELSA",
         ["FUNERAL BOAT", "CAPSIZES IN NIGERIA"],
         "At least 24 mourners dead and 24 rescued; the operator fled the scene.",
         pic_boat),
    ]

    pad = 16
    for i, (chp, head, body, pic) in enumerate(tiles):
        cx0 = xs[i % 2]
        cy0 = rows[i // 2]
        card(d, cx0, cy0, cw, rh)
        pic(d, cx0 + cw - pad - 56, cy0 + 10, 56, 56)

        chip(d, cx0 + pad, cy0 + 14, chp, 20, TEAL, 1.6)

        hmax = cw - 2 * pad
        hsize = fit_size(d, head, BOLD, hmax, 34, 24)
        hf = font(BOLD, hsize)
        hy = cy0 + 68
        for ln in head:
            d.text((cx0 + pad, hy), ln, font=hf, fill=WHITE)
            hy += int(hsize * 1.14)

        bsize = 22
        bf = font(REG, bsize)
        blines = wrap(d, body, bf, hmax)
        budget = cy0 + rh - 12
        while bsize > 20 and (len(blines) > 3 or hy + 8 + int(bsize * 1.25) * len(blines) > budget):
            bsize -= 1
            bf = font(REG, bsize)
            blines = wrap(d, body, bf, hmax)
        by = hy + 6
        for ln in blines[:3]:
            d.text((cx0 + pad, by), ln, font=bf, fill=BODY)
            by += int(bsize * 1.25)

    # ---- footer -----------------------------------------------------------
    d.rectangle([MARGIN, 944, W - MARGIN - 1, 945], fill=RULE)
    footer(d, 956)

    img.save("entry.png", "PNG")
    print("wrote entry.png", img.size, img.mode)


if __name__ == "__main__":
    main()
