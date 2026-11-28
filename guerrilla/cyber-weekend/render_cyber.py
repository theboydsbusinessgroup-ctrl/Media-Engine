"""Render the Cyber Weekend decks (PIL only, deterministic, no network).

Style (fonts, palette, layout language) reused from media-cdn holiday-push-2026/src/render.py.
Run: python3 render_cyber.py
"""
import json, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GELASIO = os.path.join(HERE, "fonts", "Gelasio[wght].ttf")  # vendored, SIL OFL (fonts/OFL.txt)
INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
LN = ["lnum"]  # lining figures: Gelasio defaults to old-style digits

THEMES = {
    "green":    {"bg": ((14, 44, 35), (8, 26, 21)), "ink": (244, 238, 227), "accent": (201, 164, 92), "muted": (190, 200, 190)},
    "burgundy": {"bg": ((74, 20, 27), (38, 10, 14)), "ink": (246, 238, 228), "accent": (214, 176, 104), "muted": (220, 196, 190)},
    "midnight": {"bg": ((18, 24, 44), (8, 10, 20)), "ink": (242, 238, 230), "accent": (214, 180, 110), "muted": (186, 190, 206)},
}
SIZES = {"tall": (1080, 1920), "feed": (1080, 1350)}
# (top, bottom) safe margins per format
SAFE = {"tall": (200, 260), "feed": (110, 110)}


def serif(size):
    if not os.path.exists(GELASIO):
        raise FileNotFoundError(f"Brand font missing: {GELASIO}")
    f = ImageFont.truetype(GELASIO, size)
    f.set_variation_by_name("Bold")  # raises if unavailable; no silent fallback
    return f


def sans(size, weight="Medium"):
    return ImageFont.truetype(INTER.format(weight), size)


def gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        d.line((0, y, w, y), fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img


def wrap(d, text, font, maxw):
    lines, line = [], ""
    for wd in text.split(" "):
        trial = (line + " " + wd).strip()
        if d.textlength(trial, font=font, features=LN) <= maxw or not line:
            line = trial
        else:
            lines.append(line)
            line = wd
    lines.append(line)
    return lines


def arrow(s):
    return s.replace("->", "→")


def layout(d, slide, s, w, M, draw=None, y0=0, t=None):
    """Lay out one slide at scale s. Returns end y. Draws if draw given."""
    maxw = w - 2 * M
    y = y0
    def block(text, font, fill, gap, spacing=1.15, center=False, indent=0):
        nonlocal y
        for ln in wrap(d, text, font, maxw - indent):
            if draw:
                x = M + indent + ((maxw - indent - d.textlength(ln, font=font, features=LN)) / 2 if center else 0)
                draw.text((x, y), ln, font=font, fill=fill, features=LN)
            y += int(font.size * spacing)
        y += gap
    block(arrow(slide["headline"]), serif(int(96 * s)), t["ink"] if t else None, int(30 * s), 1.12)
    if draw:
        draw.line((M, y, M + int(140 * s), y), fill=t["accent"], width=5)
    y += int(44 * s)
    if "sub" in slide:
        block(slide["sub"], sans(int(46 * s)), t["muted"] if t else None, int(40 * s), 1.25)
    for it in slide.get("list", []):
        f = sans(int(50 * s))
        if draw:
            draw.ellipse((M, y + int(20 * s), M + int(18 * s), y + int(38 * s)), fill=t["accent"])
        block(it, f, t["ink"] if t else None, int(30 * s), 1.22, indent=int(48 * s))
    if "price" in slide:
        pf = sans(int(60 * s), "Bold")
        txt = arrow(slide["price"])
        pw = d.textlength(txt, font=pf, features=LN)
        ph = int(120 * s)
        if draw:
            draw.rounded_rectangle((M, y, M + pw + int(80 * s), y + ph), radius=ph // 2, fill=t["accent"])
            draw.text((M + int(40 * s), y + (ph - pf.size) // 2 - int(4 * s)), txt, font=pf, fill=(20, 20, 20), features=LN)
        y += ph + int(40 * s)
    if "small" in slide:
        block(slide["small"], sans(int(36 * s), "SemiBold"), t["accent"] if t else None, 0, 1.3)
    return y


def render(slide, theme, fmt, idx, total):
    w, h = SIZES[fmt]
    t = THEMES[theme]
    img = gradient(w, h, *t["bg"])
    d = ImageDraw.Draw(img)
    top, bot = SAFE[fmt]
    avail = h - top - bot
    M = 100
    s = 1.0
    while s > 0.4 and layout(d, slide, s, w, M) > avail:
        s -= 0.04
    bh = layout(d, slide, s, w, M)
    y0 = top + (avail - bh) // 2
    layout(d, slide, s, w, M, draw=d, y0=y0, t=t)
    r, gap = 7, 26
    x0 = (w - (total - 1) * gap) / 2
    yb = h - (150 if fmt == "tall" else 60)
    for i in range(total):
        c = t["accent"] if i == idx else t["muted"]
        d.ellipse((x0 + i * gap - r, yb - r, x0 + i * gap + r, yb + r), fill=c if i == idx else None, outline=c, width=2)
    return img


def main():
    decks = json.load(open(os.path.join(HERE, "decks.json"), encoding="utf-8"))
    for fmt in SIZES:
        os.makedirs(os.path.join(HERE, fmt), exist_ok=True)
    for name, deck in decks.items():
        n = len(deck["slides"])
        for i, sl in enumerate(deck["slides"]):
            for fmt in SIZES:
                render(sl, deck["theme"], fmt, i, n).save(os.path.join(HERE, fmt, f"{name}_s{i + 1}.png"), optimize=True)
        print("done", name)


if __name__ == "__main__":
    main()
