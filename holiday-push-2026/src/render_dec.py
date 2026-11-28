"""Dec part of the holiday push: render content_dec.DECKS to slides, pins and reels."""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from content_dec import DECKS

OUT = os.environ.get("OUT_DIR", os.path.join(os.path.dirname(__file__), "out_dec"))
SRC = os.path.join(os.path.dirname(__file__), "src")
W, H = 1080, 1920

GELASIO = "/usr/share/fonts/truetype/google-fonts/ofl/gelasio/Gelasio[wght].ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"

THEMES = {
    "green":    {"bg": ((14, 44, 35), (8, 26, 21)), "ink": (244, 238, 227), "accent": (201, 164, 92), "muted": (190, 200, 190), "card": (90, 26, 31)},
    "burgundy": {"bg": ((74, 20, 27), (38, 10, 14)), "ink": (246, 238, 228), "accent": (214, 176, 104), "muted": (220, 196, 190), "card": (14, 44, 35)},
    "midnight": {"bg": ((18, 24, 44), (8, 10, 20)), "ink": (242, 238, 230), "accent": (214, 180, 110), "muted": (186, 190, 206), "card": (74, 20, 27)},
    "cream":    {"bg": ((246, 242, 235), (236, 229, 218)), "ink": (24, 24, 24), "accent": (168, 92, 30), "muted": (90, 88, 84), "card": (255, 255, 255)},
}
MENU_COLORS = {"green": (14, 44, 35), "burgundy": (90, 26, 31), "midnight": (18, 24, 44)}


def serif(size, weight="Bold"):
    f = ImageFont.truetype(GELASIO, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def sans(size, weight="Medium"):
    return ImageFont.truetype(INTER.format(weight), size)


def gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h), top)
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = c
    return img


_grad_cache = {}


def base(theme, w=W, h=H):
    key = (theme, w, h)
    if key not in _grad_cache:
        t = THEMES[theme]
        _grad_cache[key] = gradient(w, h, *t["bg"])
    return _grad_cache[key].copy()


def wrap(draw, text, font, maxw):
    out = []
    for para in text.split("\n"):
        words, line = para.split(" "), ""
        for wd in words:
            trial = (line + " " + wd).strip()
            if draw.textlength(trial, font=font) <= maxw:
                line = trial
            else:
                if line:
                    out.append(line)
                line = wd
        out.append(line)
    return out


def text_block(draw, xy, text, font, fill, maxw, spacing=1.18, align="left"):
    x, y = xy
    lines = wrap(draw, text, font, maxw)
    lh = int(font.size * spacing)
    for ln in lines:
        if align == "center":
            lw = draw.textlength(ln, font=font)
            draw.text((x + (maxw - lw) / 2, y), ln, font=font, fill=fill)
        else:
            draw.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def brand(draw, t, w, h, scale=1.0):
    f = sans(int(26 * scale), "SemiBold")
    label = "THE BOYD'S BAR  ·  BEHIND THE BAR"
    lw = draw.textlength(label, font=f)
    draw.text(((w - lw) / 2, int(110 * scale)), label, font=f, fill=t["muted"])


def cover_img(which, maxw, maxh):
    p = os.path.join(SRC, "kit_cover_tall.jpg" if which == "kit" else "mbos_cover_tall.jpg")
    im = Image.open(p).convert("RGB")
    im.thumbnail((maxw, maxh), Image.LANCZOS)
    return im


def comp(img, im, xy):
    if img.mode != "RGBA":
        img.paste(im.convert("RGB"), xy, im if im.mode == "RGBA" else None)
        return
    tmp = Image.new("RGBA", img.size, (0, 0, 0, 0))
    tmp.paste(im.convert("RGBA"), xy)
    img.alpha_composite(tmp)


def paste_shadow(img, im, xy):
    x, y = xy
    sh = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.rectangle((30, 30, 30 + im.width, 30 + im.height), fill=(0, 0, 0, 140))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    comp(img, sh, (x - 30 + 10, y - 30 + 16))
    comp(img, im, (x, y))


def render_slide(slide, theme, w=W, h=H, scale=1.0, idx=0, total=1):
    t = THEMES[theme]
    canvas = base(theme, w, h).convert("RGBA")
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    M = int(90 * scale)
    maxw = w - 2 * M
    k = slide["kind"]
    if k == "hook":
        y = int(560 * scale)
        y = text_block(d, (M, y), slide["eyebrow"], sans(int(34 * scale), "SemiBold"), t["accent"], maxw) + int(24 * scale)
        y = text_block(d, (M, y), slide["title"], serif(int(104 * scale)), t["ink"], maxw, 1.12) + int(40 * scale)
        d.line((M, y, M + int(140 * scale), y), fill=t["accent"], width=max(3, int(5 * scale)))
        y += int(44 * scale)
        text_block(d, (M, y), slide["sub"], sans(int(44 * scale), "Medium"), t["muted"], maxw)
    elif k in ("list", "steps"):
        y = int(300 * scale)
        y = text_block(d, (M, y), slide["title"], serif(int(92 * scale)), t["ink"], maxw, 1.12) + int(64 * scale)
        if k == "list":
            f = sans(int(50 * scale), "Medium")
            for it in slide["items"]:
                d.ellipse((M, y + int(22 * scale), M + int(18 * scale), y + int(40 * scale)), fill=t["accent"])
                y = text_block(d, (M + int(48 * scale), y), it, f, t["ink"], maxw - int(48 * scale), 1.22) + int(38 * scale)
        else:
            fn, fh, fb = serif(int(48 * scale)), sans(int(50 * scale), "SemiBold"), sans(int(40 * scale), "Regular")
            for i, (head, body) in enumerate(slide["items"], 1):
                r = int(38 * scale)
                d.ellipse((M, y, M + 2 * r, y + 2 * r), outline=t["accent"], width=max(2, int(3 * scale)))
                num = str(i)
                nw = d.textlength(num, font=fn)
                d.text((M + r - nw / 2, y + int(6 * scale)), num, font=fn, fill=t["accent"])
                x2 = M + 2 * r + int(30 * scale)
                yy = text_block(d, (x2, y + int(6 * scale)), head, fh, t["ink"], maxw - (x2 - M), 1.18)
                yy = text_block(d, (x2, yy + int(4 * scale)), body, fb, t["muted"], maxw - (x2 - M), 1.25)
                y = max(yy, y + 2 * r) + int(50 * scale)
    elif k == "menu":
        cw, ch = int(760 * scale), int(900 * scale)
        cx, cy = (w - cw) // 2, int(360 * scale)
        col = MENU_COLORS.get(slide.get("color", "green"))
        sh = Image.new("RGBA", (cw + 80, ch + 80), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle((40, 40, 40 + cw, 40 + ch), fill=(0, 0, 0, 150))
        sh = sh.filter(ImageFilter.GaussianBlur(22))
        comp(img, sh, (cx - 40 + 12, cy - 40 + 20))
        d.rectangle((cx, cy, cx + cw, cy + ch), fill=col)
        g = (201, 164, 92)
        d.rectangle((cx + 22, cy + 22, cx + cw - 22, cy + ch - 22), outline=g, width=2)
        d.rectangle((cx + 32, cy + 32, cx + cw - 32, cy + ch - 32), outline=g, width=1)
        y = cy + int(110 * scale)
        y = text_block(d, (cx + 60, y), slide["title"], serif(int(70 * scale)), (246, 240, 230), cw - 120, 1.12, "center") + int(30 * scale)
        d.line((cx + cw / 2 - 60, y, cx + cw / 2 + 60, y), fill=g, width=2)
        y += int(60 * scale)
        items = slide["items"]
        f = serif(int(46 * scale), "Regular")
        for i, it in enumerate(items):
            if i == len(items) - 1 and slide.get("note"):
                nf = sans(int(22 * scale), "SemiBold")
                note = "ZERO PROOF"
                nw = d.textlength(note, font=nf)
                d.text((cx + (cw - nw) / 2, y), note, font=nf, fill=g)
                y += int(40 * scale)
            y = text_block(d, (cx + 50, y), it, f, (246, 240, 230), cw - 100, 1.15, "center") + int(44 * scale)
        foot = sans(int(30 * scale), "Medium")
        label = slide.get("foot", "From the Holiday Cocktail Party Menu Kit")
        lw = d.textlength(label, font=foot)
        d.text(((w - lw) / 2, cy + ch + int(60 * scale)), label, font=foot, fill=t["muted"])
    elif k == "big":
        y = int(420 * scale)
        y = text_block(d, (M, y), slide["eyebrow"], sans(int(34 * scale), "SemiBold"), t["accent"], maxw, align="center") + int(20 * scale)
        y = text_block(d, (M, y), slide["big"], serif(int(210 * scale)), t["accent"], maxw, 1.05, "center") + int(40 * scale)
        y = text_block(d, (M, y), slide["title"], serif(int(64 * scale)), t["ink"], maxw, 1.16, "center") + int(40 * scale)
        text_block(d, (M, y), slide["body"], sans(int(40 * scale), "Regular"), t["muted"], maxw, 1.3, "center")
    elif k == "cta":
        y = int(230 * scale)
        y = text_block(d, (M, y), slide["eyebrow"], sans(int(30 * scale), "SemiBold"), t["accent"], maxw, align="center") + int(18 * scale)
        y = text_block(d, (M, y), slide["title"], serif(int(70 * scale)), t["ink"], maxw, 1.12, "center") + int(26 * scale)
        y = text_block(d, (M + int(30 * scale), y), slide["body"], sans(int(34 * scale), "Regular"), t["muted"], maxw - int(60 * scale), 1.3, "center") + int(40 * scale)
        im = cover_img(slide["cover"], int(560 * scale), int(840 * scale))
        paste_shadow(img, im, ((w - im.width) // 2, y))
        y += im.height + int(50 * scale)
        pf = sans(int(44 * scale), "Bold")
        price = slide["price"]
        pw = d.textlength(price, font=pf)
        bx0, bx1 = (w - pw) / 2 - int(40 * scale), (w + pw) / 2 + int(40 * scale)
        d.rounded_rectangle((bx0, y, bx1, y + int(92 * scale)), radius=int(46 * scale), fill=t["accent"])
        dark = (20, 20, 20) if theme != "cream" else (255, 255, 255)
        d.text(((w - pw) / 2, y + int(20 * scale)), price, font=pf, fill=dark)
        y += int(120 * scale)
        ff = sans(int(36 * scale), "SemiBold")
        fw = d.textlength(slide["foot"] + "  →", font=ff)
        d.text(((w - fw) / 2, y), slide["foot"] + "  →", font=ff, fill=t["ink"])
    box = img.getbbox()
    if box:
        top, bottom = int(230 * scale), h - int(330 * scale)
        dy = int((top + bottom) / 2 - (box[1] + box[3]) / 2)
        dy = max(dy, top - box[1]) if box[3] - box[1] < bottom - top else top - box[1]
        shifted = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        shifted.paste(img, (0, dy))
        img = shifted
    canvas.alpha_composite(img)
    img = canvas.convert("RGB")
    d = ImageDraw.Draw(img)
    brand(d, t, w, h, scale)
    # page dots
    if total > 1:
        r, gap = int(7 * scale), int(26 * scale)
        x0 = (w - (total - 1) * gap) / 2
        yb = h - int(140 * scale) if h == H else h - int(70 * scale)
        for i in range(total):
            fill = t["accent"] if i == idx else t["muted"]
            d.ellipse((x0 + i * gap - r, yb - r, x0 + i * gap + r, yb + r), fill=fill if i == idx else None, outline=fill, width=2)
    return img


def render_pin(deck):
    """1000x1500 pin: hook + key list + product cover + price."""
    theme = deck["theme"]
    t = THEMES[theme]
    w, h = 1000, 1500
    img = base(theme, w, h)
    d = ImageDraw.Draw(img)
    M = 70
    hook = deck["slides"][0]
    y = 70
    y = text_block(d, (M, y), hook["eyebrow"], sans(28, "SemiBold"), t["accent"], w - 2 * M, align="center") + 14
    y = text_block(d, (M, y), hook["title"].replace("\n", " "), serif(76), t["ink"], w - 2 * M, 1.1, "center") + 26
    # pick the first list/steps slide for bullets
    body = next((s for s in deck["slides"][1:] if s["kind"] in ("list", "steps", "menu")), None)
    items = []
    if body:
        if body["kind"] == "steps":
            items = [a for a, _ in body["items"]]
        else:
            items = body["items"]
    f = sans(32, "Medium")
    for it in items[:4]:
        d.ellipse((M + 40, y + 13, M + 52, y + 25), fill=t["accent"])
        y = text_block(d, (M + 72, y), it, f, t["ink"], w - 2 * M - 80, 1.2) + 12
    y += 18
    cta = deck["slides"][-1]
    im = cover_img(cta["cover"], 440, h - y - 190)
    paste_shadow(img, im, ((w - im.width) // 2, y))
    y += im.height + 34
    pf = sans(36, "Bold")
    price = cta["price"]
    pw = d.textlength(price, font=pf)
    d.rounded_rectangle(((w - pw) / 2 - 34, y, (w + pw) / 2 + 34, y + 74), radius=37, fill=t["accent"])
    d.text(((w - pw) / 2, y + 16), price, font=pf, fill=(20, 20, 20) if theme != "cream" else (255, 255, 255))
    return img


def make_reel(paths, music, out, per=3.6, fade=0.5):
    n = len(paths)
    inputs = []
    for p in paths:
        inputs += ["-loop", "1", "-t", f"{per + fade:.2f}", "-i", p]
    inputs += ["-i", music]
    filt, last = [], "[0:v]"
    for i in range(n):
        filt.append(f"[{i}:v]scale=1080:1920,format=yuv420p,setsar=1[v{i}]")
    last = "[v0]"
    for i in range(1, n):
        off = i * per
        filt.append(f"{last}[v{i}]xfade=transition=fade:duration={fade}:offset={off - fade * 0 + 0:.2f}[x{i}]")
        last = f"[x{i}]"
    total = n * per + fade
    # gentle zoom is costly; keep static crossfades
    filt.append(f"{last}trim=duration={total:.2f},fps=30[vout]")
    filt.append(f"[{n}:a]atrim=duration={total:.2f},afade=t=in:d=0.6,afade=t=out:st={total - 1.2:.2f}:d=1.2,volume=0.9[aout]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
           "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    music = os.environ.get("MUSIC", os.path.join(OUT, "music.wav"))
    only = sys.argv[1:]
    for deck in DECKS:
        if only and deck["id"] not in only:
            continue
        n = len(deck["slides"])
        paths = []
        for i, s in enumerate(deck["slides"]):
            im = render_slide(s, deck["theme"], idx=i, total=n)
            p = os.path.join(OUT, f"{deck['id']}_s{i + 1}.jpg")
            im.save(p, quality=88)
            paths.append(p)
        pin = render_pin(deck)
        pin.save(os.path.join(OUT, f"{deck['id']}_pin.jpg"), quality=92)
        if os.path.exists(music):
            make_reel(paths, music, os.path.join(OUT, f"{deck['id']}_reel.mp4"))
        print("done", deck["id"])
